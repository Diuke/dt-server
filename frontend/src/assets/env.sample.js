(function (window) {
    window['env'] = window['env'] || {};
  
    // Environment variables
    window['env']['backend_base_url'] = '${BACKEND_BASE_URL}';
    window['env']['api_key'] = '${BACKEND_API_KEY}';
  })(this);