## Exhaustive Numbered Requirements for Bitcoin's Future and Destiny Page

### 1. **Hard Cap Display (21 Million BTC)**
- **Purpose:** Present Bitcoin’s fixed supply to underscore scarcity.
- **UI/UX:** Prominently display, preferably in a “key metric” widget with static explanatory tooltip explaining why it matters.
- **Backend/Data:** Static value (`21_000_000`); may be hardcoded.
- **Tooltip/Help:** “Bitcoin’s supply is algorithmically capped at 21 million coins.”
- **No API call required.**

### 2. **Show Current Bitcoin in Circulation and Remaining to Mine**
- **Purpose:** Visually and numerically show the total coins mined, circulating supply, and how many are left to mine.
- **Data Sourcing:**
  - **Total Mined & Circulating:** Pull from sources like blockchain.com, CoinMetrics, or CoinMarketCap [1].
  - **Endpoint Examples:**
    - `https://api.blockchain.com/v3/exchange/tickers/BTC-USD` (may provide circulating supply field).
    - `https://coinmarketcap.com/api/` (use `/cryptocurrency/info` for current stats).
- **Calculations:** `Remaining = 21,000,000 - Circulating/Mined`
- **Session State:** Cache parsed values, refresh only on user request or fixed intervals.
- **Widget:** Use metric cards; add info button for definitions.

### 3. **Bitcoins Left to Be Mined Over Time (Projection to 2140)**
- **Purpose:** Convey long tail of remaining supply via time-series visualization.
- **Input/Params:** Use historic mining data, halving epochs.
- **Data Sources:**
  - Historic and future halving schedules from blockchain.com, CoinMetrics, Binance [2][3].
- **Visualization:** Plot with plotly/altair—a line or area chart (x-axis: years, y-axis: BTC left).
- **Annotations:** Mark halving dates, projected end (2140).
- **Session State:** Store user viewing range (e.g., slider for choosing range between 2009–2140).

### 4. **Bitcoin Mining Rate, Block Rewards & Halving Events Visualization**
- **Purpose:** Demonstrate how mining slows due to halvings, and show block reward evolution.
- **Data Sourcing:**
  - Block reward history and halving epochs: CoinMetrics, blockchain.com’s charts or from timeline sites [2][3][4].
- **Visualization:** Multi-line plot with:
  - Mining rate per year,
  - Block reward per halving,
  - Vertical lines/annotations for each halving event.
- **Tooltip:** Definitions for “block reward,” “halving.”
- **Session State:** Allow user to select specific halving event or zoom.

### 5. **Mempool Data (Live and Historic)**
- **Purpose:** Visualize mempool congestion and relate it to mining activity and user adoption.
- **Data Sources:**
  - Use mempool.space API—for mempool size, fee rates, pending transactions [5][6].
    - Example: `https://mempool.space/api/mempool` (size); `https://mempool.space/api/v1/fees/recommended` (fee rates).
  - Alternatively, Bitquery for advanced mempool analytics [6].
- **Visualization:** Real-time line/bar graph—X: time, Y: tx count or megabytes.
- **Session State:** Store fetched mempool data; auto-update regularly (every 2-5 minutes).
- **Help:** Link to API docs for further troubleshooting.

### 6. **Active Bitcoin Wallet Addresses Over Time**
- **Purpose:** Quantify adoption by showing unique non-zero addresses through time.
- **Data Sources:**
  - Coin Metrics, Blockchain.com API, and/or BlockCypher [7].
    - Coin Metrics endpoint: `/timeseries/asset-metrics?metrics=AdrActCnt`.
    - BlockCypher: `/v1/btc/main/addrs` (for specific addresses).
- **Visualization:** Time-series plot (addresses on y-axis, time on x-axis).
- **Session State:** Allow filtering by year, animate address count evolution.
- **Tooltip:** “Active wallets: Addresses with non-zero balance.”

### 7. **Global Bitcoin Adoption and User Growth**
- **Purpose:** Spatially illustrate adoption trends by region, country, or globally.
- **Data Sources:**
  - Triple-A ownership dataset,
  - CoinMarketCap for user stats,
  - Published reports (as fallback; accept update via CSV upload).
- **Visualization:** Interactive choropleth world map and/or ranked bar chart.
- **Session State:** Store dataset, allow filtering by region/period.
- **Tooltip:** “Adoption shown as % population or total owners.”

### 8. **Illiquid Bitcoin Supply Estimation**
- **Purpose:** Illustrate proportion held long-term or inaccessible, emphasizing “real” liquid supply.
- **Data Sources:**
  - Coin Metrics (metrics: `IlliquidSupply`, `LiquidSupply`); research estimates (manual update may be required).
- **Visualization:** Pie/donut or stacked bar (liquid vs. illiquid, lost, “hodled”).
- **Session State:** Store calculation, allow toggle to update on refresh.

### 9. **Holder Behavior: Long-term vs. Short-term**
- **Purpose:** Classify and plot “diamond hands” (holding >1yr) vs. short-term holders.
- **Data Sources:**
  - Coin Metrics, Glassnode (public dashboard/stats).
  - Use ratio/percentage of coins not moved for >1yr vs. moved recently.
- **Visualization:** Area or bar chart over time.
- **Session State:** Widget to select lookback window.

### 10. **Sell vs Hold Behavior Timeline**
- **Purpose:** Show visually, over time, when holders sold or held en masse, cross-referencing address/productivity data.
- **Data:** Synthesize metrics from #6 (wallets), #9 (holder types). Optionally, use on-chain “coin age destroyed” metrics if available.
- **Visualization:** Composite time-series chart with correlated overlays.
- **Session State:** Allow brushing/selection; cross-highlight with holders/wallets visual.

### 11. **Institutional and Key Holder Accumulation**
- **Purpose:** Quantify portion of supply held by institutions, strategic reserves, and largest wallets.
- **Data Sources:** Public filings, on-chain analytics aggregators. If no API, request manual upload of CSV (explained to sponsor).
- **Visualization:** “Call-out” cards and overlay on supply chart.
- **Session State:** Store data; annotate with footnotes if based on external research.

### 12. **Transaction Fees and Congestion**
- **Purpose:** Show periods of high transaction fees, relating to adoption and mempool spikes.
- **Data Sources:**
  - Mempool.space API (`/fees/mempool-blocks`), blockchain.com API (median/mean fee time-series).
- **Visualization:** Dual-axis time series (X: time, Y(left): fees, Y(right): mempool size).
- **Session State:** Store displayed range.

### 13. **Key Scarcity Infographic / Dashboard**
- **Purpose:** Aggregate top-line metrics (hard cap, mined, liquid, illiquid supply, active wallets) in visually arresting dashboard or infographic.
- **Data:** Pull metrics from above in real-time.
- **Design:** Single area with big numbers, graphical elements, and tooltips linking to relevant visualizations.

### 14. **Glossary / Help Section**
- **Purpose:** Ensure users can access definitions and explanations for cryptographic/financial terms without leaving the app.
- **Method:** Populate tooltips, Streamlit expanders, or modal pop-ups for:
  - Mining, Halving, Block Reward, Mempool, Wallet Address, Illiquid Supply, etc.
- **Content:** Write concise, user-friendly definitions; link to relevant APIs/doc sites as needed.

### 15. **Scenario Simulator (Optional), In-Session**
- **Purpose:** Allow user to alter parameters such as adoption rate, holding patterns, or transaction fee assumptions; project hypothetical outcomes for supply/demand, price.
- **Implementation:**
  - Use Streamlit widgets (sliders/select boxes) to adjust variables (adoption%, sell/hold ratio, fee assumptions).
  - Calculations run in session state; update projection charts on-the-fly.
- **Backend:** Computation in Python; defaults based on actual data; session state preserves selections within user session.
- **Help:** Provide quick “reset to baseline” button; document default values and assumptions in tooltip.

### General Technical and Coding Requirements

- **All data retrieval:** Use session state to store and manage fetched or computed values across reruns per user session. Never rely on app-level globals or file system persistence [8][9][10].
- **Visualization libraries:** Use `plotly` or `altair` for rich, interactive charts.
- **Caching:** Use `st.cache_data` (Streamlit) for any expensive or rate-limited API calls—scoped per-session, reset on app redeploy [8][9].
- **UI:** Prefer metric cards for single-value stats; line/area for timeseries; pie or donut for share; bar/column for rankings.
- **Accessibility:** All visualizations must include tooltips or help text for non-obvious terms.
- **Error handling:** On API failure, display informative placeholder message with retry logic and doc links for data sources.

#### **Key Public APIs & Example Endpoints**

| Requirement         | API / Data Source                                                      | Example                           |
|---------------------|-----------------------------------------------------------------------|-----------------------------------|
| Current supply      | blockchain.com, CoinMarketCap, CoinMetrics                            | `/v3/exchange/tickers/BTC-USD`    |
| Mempool, fees       | mempool.space REST/WebSocket, Bitquery                                | `/api/mempool`, `/api/fees`       |
| Active wallets      | Coin Metrics, Blockchain.com, BlockCypher                             | `/timeseries/asset-metrics`       |
| Adoption by region  | Triple-A, CSV/manual report input                                     | —                                 |
| Block rewards       | CoinMetrics, blockchain.com, timeline websites                        | `/api/block-reward-history`       |
| Holder stats        | CoinMetrics, Glassnode (public), CSV/manual update as fallback        | —                                 |

**Note:** Any APIs not directly accessible can be replaced with CSV upload, with clear instructions to sponsor on data format.

**Session State:** All session variables must be scoped per user, with comprehensive utilization of Streamlit’s session and caching mechanisms to avoid data loss between reruns and to ensure stateless operation on Streamlit Community Cloud [8][9][10].

[1] https://bitcoin.stackexchange.com/questions/118628/where-can-i-get-a-free-rpc-public-rpc-to-access-bitcoin-mempool
[2] https://www.bitget.com/academy/bitcoin-halving-history-timeline-date-price-chart
[3] https://www.binance.com/en/square/post/5882739178050
[4] https://blog.kraken.com/wp-content/uploads/2020/02/Bitcoin_Halving_F_v09_1.pdf
[5] https://bitcoin.stackexchange.com/questions/118837/whats-the-fastest-websocket-bitcoin-provider-to-access-mempool-data
[6] https://bitquery.io/blog/maximizing-crypto-gains-mempool-bitquery-token-price-predictions
[7] https://bitcoin.stackexchange.com/questions/76088/simple-address-check-via-api
[8] https://docs.kanaries.net/topics/Streamlit/streamlit-session-state
[9] https://docs.streamlit.io/get-started/fundamentals/advanced-concepts
[10] https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
[11] https://www.linkedin.com/posts/sreejabethu_github-sreejabethurealtime-stock-market-analysis-visualization-activity-7224894652863164418-uviG
[12] https://blog.streamlit.io/best-practices-for-building-genai-apps-with-streamlit/
[13] https://www.ijsdr.org/papers/IJSDR2405202.pdf
[14] https://www.youtube.com/watch?v=jP15RFcpysg
[15] https://www.packtpub.com/en-in/data/concept/data-visualization
[16] https://developer.bitcoin.org/reference/rpc/getaddressinfo.html
[17] https://av.tib.eu/media/53307
[18] https://bitcoin.stackexchange.com/questions/98741/how-can-i-build-my-own-get-address-transactions-api
[19] https://discuss.streamlit.io/t/streamlit-best-practices/57921
[20] https://www.youtube.com/watch?v=628TPxDD4I8