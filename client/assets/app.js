const app = Vue.createApp({
  data() {
    return {
      appName: "Product Scraper",
      baseUrl: "http://127.0.0.1:8000",
      productUrl: "/api/products/",
      brandName: "iPhone",
      searchQuery: "",   // New property for the search term
      fields: ["name", "asin", "image", "brand"],
      currentSort: "name",
      currentSortDir: "asc",
      productsList: [],
      currentPage: 1,
      pageSize: 5,
    };
  },
  methods: {
    // Sorting handler
    sort(s) {
      if (s === this.currentSort) {
        this.currentSortDir = this.currentSortDir === "asc" ? "desc" : "asc";
      }
      this.currentSort = s;
    },

    // Fetch products by brand and search query, with pagination
    async fetchProducts(page = 1) {
      if (!this.brandName) {
        alert("Please enter a brand name.");
        return;
      }

      try {
        // Add search query to the API request parameters
        const res = await fetch(
          `${this.baseUrl}${this.productUrl}?brand__name=${this.brandName}&page=${page}&page_size=${this.pageSize}&search=${this.searchQuery}`,
          { mode: "cors" }
        );

        if (res.ok) {
          const result = await res.json();
          this.productsList = result.results; // assuming paginated data in `results`
          this.currentPage = page; // set current page
        } else {
          throw new Error("Failed to fetch products. Check your brand name and search term.");
        }
      } catch (error) {
        console.error(error);
        alert("Error fetching products: " + error.message);
      }
    },
  },

  computed: {
    // Returns sorted list of products
    sortedProductsList() {
      return this.productsList.sort((a, b) => {
        let modifier = this.currentSortDir === "desc" ? -1 : 1;
        if (a[this.currentSort] < b[this.currentSort]) return -1 * modifier;
        if (a[this.currentSort] > b[this.currentSort]) return 1 * modifier;
        return 0;
      });
    },
  },

  mounted() {
    // Fetch initial products only if `brandName` is already set
    if (this.brandName) {
      this.fetchProducts();
    }
  },
});
