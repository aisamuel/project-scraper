const app = Vue.createApp({
  data() {
    return {
      appName: "Product Scraper",
      baseUrl: "http://127.0.0.1:8000",
      productUrl: "/api/products/",
      brandUrl: "/api/brands/", 
      selectedBrand: "",
      brandsList: [], 
      searchQuery: "",
      fields: ["name", "asin", "image", "brand"],
      currentSort: "name",
      currentSortDir: "asc",
      productsList: [],
      currentPage: 1,
      pageSize: 10,
    };
  },
  methods: {
    // Fetch all brands from the API
    async fetchBrands() {
      console.log("Fetching brands...");

      try {
        const res = await fetch(`${this.baseUrl}${this.brandUrl}`);
        if (!res.ok) throw new Error("Failed to fetch brands.");

        const result = await res.json();
        console.log("Brands received:", result);

        this.brandsList = result.results;

        if (this.brandsList.length > 0) {
          this.selectedBrand = this.brandsList[0].name; 
          console.log("Default brand selected:", this.selectedBrand);
          this.fetchProducts(1);
        }
      } catch (error) {
        console.error("Error fetching brands:", error);
      }
    },

    async fetchProducts(page = 1, allBrands = false) {
      console.log(`fetchProducts() called with page: ${page}, Brand: ${this.selectedBrand}`);
    
      // ✅ Adjust API URL based on whether "ALL" is selected
      let apiUrl = `${this.baseUrl}${this.productUrl}?page=${page}&page_size=${this.pageSize}&search=${this.searchQuery}`;
    
      if (!allBrands) {
        apiUrl += `&brand__name=${encodeURIComponent(this.selectedBrand)}`;
      }
    
      try {
        const res = await fetch(apiUrl, { mode: "cors" });
    
        if (res.ok) {
          const result = await res.json();
          console.log("Products received:", result);
          this.productsList = result.results;
          this.currentPage = page;
        } else {
          throw new Error("Failed to fetch products.");
        }
      } catch (error) {
        console.error("Error fetching products:", error);
      }
    },
    


    updateBrand(event) {
      console.log(`New brand selected (before update): ${event.target.value}`);
  
      this.selectedBrand = event.target.value;
  
      this.$nextTick(() => {
        console.log(`Updated selectedBrand: ${this.selectedBrand}, calling fetchProducts...`);
        if (this.selectedBrand === "ALL") {
          this.fetchProducts(1, allBrands=true);
        } else {
          this.fetchProducts(1);
        }
      });
    },

    sort(s) {
      if (s === this.currentSort) {
        this.currentSortDir = this.currentSortDir === "asc" ? "desc" : "asc";
      }
      this.currentSort = s;
    },
  },

  computed: {
    sortedProductsList() {
      return this.productsList.sort((a, b) => {
        let modifier = this.currentSortDir === "desc" ? -1 : 1;
        if (a[this.currentSort] < b[this.currentSort]) return -1 * modifier;
        if (a[this.currentSort] > b[this.currentSort]) return 1 * modifier;
        return 0;
      });
    },
  },

  created() {
    console.log("Vue app mounted! Fetching brands...");
    this.fetchBrands();
  },
});
