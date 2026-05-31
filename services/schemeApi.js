const BASE_URL = "https://api.myscheme.gov.in/search/v4/schemes";

export async function fetchSchemes(state, options = {}) {
  const params = new URLSearchParams({
    lang: options.lang || "en"
  });

  if (state) {
    params.set("state", state);
  }

  if (options.central !== undefined) {
    params.set("central", String(options.central));
  }

  const headers = {
    Accept: "application/json",
    ...options.headers
  };

  if (options.apiKey) {
    headers[options.apiKeyHeader || "x-api-key"] = options.apiKey;
  }

  const response = await fetch(`${BASE_URL}?${params.toString()}`, {
    method: "GET",
    headers
  });

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;

    try {
      const errorBody = await response.json();
      message = errorBody.message || JSON.stringify(errorBody);
    } catch {
      // Some gateway failures are not JSON; keep the HTTP status message.
    }

    throw new Error(`myScheme API request failed: ${message}`);
  }

  return response.json();
}

export { BASE_URL as MYSCHEME_SEARCH_URL };
