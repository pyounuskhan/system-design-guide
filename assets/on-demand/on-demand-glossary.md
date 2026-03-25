# On-Demand Services — Glossary

| Term | Definition |
|------|-----------|
| **H3** | Uber's hexagonal hierarchical spatial index — divides earth into hexagonal cells |
| **S2** | Google's spherical geometry library — divides earth into cells on a sphere |
| **Geohash** | Base-32 encoding of latitude/longitude into a string; longer string = higher precision |
| **k-ring** | Set of hexagonal cells within k steps of a center cell (H3 neighbor query) |
| **ETA** | Estimated Time of Arrival — predicted time for driver/courier to reach destination |
| **Surge Pricing** | Dynamic price adjustment based on real-time supply/demand ratio |
| **Supply/Demand Ratio** | Available drivers divided by ride requests in a geographic cell |
| **Matching** | Pairing a rider/customer with a driver/delivery partner |
| **Dispatch** | Sending a ride/delivery offer to a selected driver |
| **Acceptance Rate** | Percentage of offers a driver accepts; low rate reduces matching priority |
| **Dead Miles** | Distance a driver travels without a passenger (to pickup, after dropoff) |
| **Batch Delivery** | One delivery partner carrying orders from multiple restaurants/merchants |
| **Contraction Hierarchy** | Graph preprocessing technique enabling ultra-fast shortest-path queries |
| **VRP** | Vehicle Routing Problem — NP-hard optimization for delivery routes |
| **CVRP** | Capacitated VRP — includes vehicle weight/volume constraints |
| **VRPTW** | VRP with Time Windows — each stop has a delivery window |
| **DVRP** | Dynamic VRP — new orders added to routes in real-time |
| **Kalman Filter** | Algorithm for smoothing noisy GPS data using predicted + observed positions |
| **Geofence** | Virtual geographic boundary; triggers events when a device enters/exits |
| **Prep Time** | Time a restaurant takes to prepare a food order |
| **SLA** | Service Level Agreement — promised delivery time to customer |
| **Fleet** | Pool of all drivers/delivery partners available on the platform |
| **Incentive** | Bonus payment to drivers for completing trips during high-demand periods |
| **Demand Prediction** | ML model forecasting ride/order volume by area and time |
| **Pre-positioning** | Moving idle drivers to areas with predicted high demand |
