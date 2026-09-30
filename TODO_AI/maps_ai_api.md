# LieppOS Maps / Navigation AI API

Target:

- **LieppOS**
- **Device:** Ulefone Armor 29 Pro Thermal
- **Codename:** GQ5012BF1

Purpose:

> Let the local LieppOS AI understand natural-language navigation requests and open the user's preferred maps application with the destination, travel mode, and route already prepared.

Example:

```text
User:
"AI, make route via Maps to Gediminas Tower."

LieppOS:
  intent = NAVIGATE
  destination = "Gediminas Tower"
  preferred_app = "google_maps"

        ↓

Google Maps opens directly on the route to Gediminas Castle Tower.
```

The LLM must not automate taps/screens unless absolutely necessary.

Preferred integration order:

```text
native Android intent / app API
        ↓
supported Maps URL / URI
        ↓
AppFunction or plugin
        ↓
UI automation only as last resort
```

---

# 1. Design Rule

Do **not** expose Google Maps directly as the AI's primary API.

The model should use a generic LieppOS navigation interface:

```text
lieppos.navigation.*
```

The operating system decides which map application handles the request.

Example:

```text
lieppos.navigation.route(
    destination = "Gediminas Tower",
    travel_mode = "DRIVING",
    preferred_app = "google_maps"
)
```

The same model request could instead launch:

```text
Organic Maps
OsmAnd
Google Maps
another installed navigation provider
```

without changing the model-facing API.

---

# 2. Core API

Initial namespace:

```text
lieppos.navigation.search
lieppos.navigation.resolve_place
lieppos.navigation.route
lieppos.navigation.start
lieppos.navigation.show
lieppos.navigation.get_preferences
lieppos.navigation.set_default_app
```

---

# 3. `lieppos.navigation.search`

Search for places.

Input:

```text
query: string
nearby: optional boolean
location_bias: optional coordinate/region
max_results: optional integer
```

Example:

```text
lieppos.navigation.search(
    query = "Gediminas Tower"
)
```

Possible structured result:

```json
{
  "results": [
    {
      "name": "Gediminas Castle Tower",
      "city": "Vilnius",
      "country": "Lithuania",
      "address": "Arsenalo g. 5, Vilnius",
      "latitude": 54.6867,
      "longitude": 25.2906,
      "provider_id": "provider-specific-id",
      "confidence": 0.98
    }
  ]
}
```

The AI should not receive provider-specific IDs unless needed.

---

# 4. `lieppos.navigation.resolve_place`

Resolve free text into a concrete place.

Input:

```text
query
optional city
optional country
optional current-location bias
```

Example:

```text
resolve_place(
    query = "Gediminas Tower",
    city = "Vilnius"
)
```

Output:

```json
{
  "status": "RESOLVED",
  "place": {
    "name": "Gediminas Castle Tower",
    "address": "Arsenalo g. 5, Vilnius",
    "latitude": 54.6867,
    "longitude": 25.2906
  }
}
```

Possible statuses:

```text
RESOLVED
AMBIGUOUS
NOT_FOUND
PROVIDER_UNAVAILABLE
```

---

# 5. Ambiguity Handling

The AI must not silently guess when several destinations are plausible.

Example:

```text
User:
"Take me to Gediminas."
```

Tool result:

```json
{
  "status": "AMBIGUOUS",
  "choices": [
    {
      "name": "Gediminas Castle Tower",
      "city": "Vilnius"
    },
    {
      "name": "Gedimino Avenue",
      "city": "Vilnius"
    }
  ]
}
```

AI response:

```text
"Do you mean Gediminas Castle Tower or Gedimino Avenue?"
```

Rules:

- obvious single result → proceed
- multiple plausible results → ask
- existing user context may disambiguate
- never invent an address

---

# 6. `lieppos.navigation.route`

Show a route but do not necessarily start turn-by-turn navigation.

Input:

```text
destination
origin = CURRENT_LOCATION by default
travel_mode
preferred_app
avoid options
```

Schema concept:

```text
lieppos.navigation.route(
    destination: Place|string,
    origin: Place|string|CURRENT_LOCATION,
    travel_mode: DRIVING|WALKING|BICYCLING|TRANSIT|DEFAULT,
    preferred_app: DEFAULT|GOOGLE_MAPS|ORGANIC_MAPS|OSMAND,
    avoid: optional set
)
```

Example:

```text
route(
    destination = "Gediminas Tower",
    travel_mode = "DRIVING",
    preferred_app = "GOOGLE_MAPS"
)
```

Expected behavior:

```text
Google Maps opens
       ↓
destination filled
       ↓
route overview displayed
       ↓
user can review route
```

---

# 7. `lieppos.navigation.start`

Start navigation when the provider supports it.

Input:

```text
destination
travel_mode
preferred_app
```

Example:

```text
lieppos.navigation.start(
    destination = "Gediminas Tower",
    travel_mode = "DRIVING"
)
```

Expected behavior:

```text
preferred navigation app opens
        ↓
route loaded
        ↓
navigation started or placed at the final provider confirmation step
```

Do not fake UI input if the provider exposes a supported deep link or intent.

---

# 8. `lieppos.navigation.show`

Open a place without creating a route.

Example:

```text
lieppos.navigation.show(
    destination = "Gediminas Tower"
)
```

Possible use:

```text
"Show Gediminas Tower on Maps."
```

Result:

```text
map opens centered on destination
```

---

# 9. Travel Modes

Initial enum:

```text
DEFAULT
DRIVING
WALKING
BICYCLING
TRANSIT
```

Future:

```text
MOTORCYCLE
EV
WHEELCHAIR
```

only if supported by the selected provider.

Unsupported mode handling:

```text
REQUESTED_MODE_UNSUPPORTED
```

Then either:

- fall back to DEFAULT if user policy allows
- ask the user
- choose another provider

---

# 10. Route Options

Potential generic options:

```text
avoid_highways
avoid_tolls
avoid_ferries
prefer_fastest
prefer_shortest
```

Do not expose an option to the model unless at least one installed provider can honor it reliably.

Example:

```text
User:
"Take me to Gediminas Tower but avoid highways."
```

Tool request:

```text
route(
    destination = "Gediminas Tower",
    travel_mode = DRIVING,
    avoid = { HIGHWAYS }
)
```

---

# 11. Provider Adapter Layer

Architecture:

```text
LLM
 ↓
LieppOS Navigation API
 ↓
Navigation Broker
 ↓
Provider Adapter
 ├── Google Maps
 ├── Organic Maps
 ├── OsmAnd
 └── future providers
```

Each adapter implements:

```text
can_search()
can_show_place()
can_show_route()
can_start_navigation()
supported_travel_modes()
supported_avoid_options()
```

---

# 12. Google Maps Adapter

Preferred integration:

```text
Android Intent
or
Google Maps URI / supported Maps URL
```

Example internal flow:

```text
destination:
"Gediminas Castle Tower, Vilnius"

travel mode:
DRIVING

        ↓

GoogleMapsAdapter

        ↓

ACTION_VIEW / supported Maps URI

        ↓

Google Maps
```

Do not rely on screen coordinates or simulated typing if a native navigation intent is available.

---

# 13. Offline Maps Adapter

LieppOS should support a privacy/offline provider such as:

```text
Organic Maps
OsmAnd
```

Example:

```text
lieppos.navigation.route(
    destination = "Gediminas Tower",
    preferred_app = "ORGANIC_MAPS"
)
```

The model should not care whether routing happens:

```text
online
offline
Google
OpenStreetMap-based
```

That is a provider concern.

---

# 14. Default Navigation Policy

Settings:

```text
Settings
 → LieppOS AI
 → Navigation
```

Options:

```text
Default app:
  [Google Maps]
  [Organic Maps]
  [OsmAnd]
  [Ask every time]

Default travel mode:
  [Driving]
  [Walking]
  [Transit]
  [Remember last]

Use current location automatically:
  [On/Off]

Resolve ambiguous places automatically:
  [Never]
  [High-confidence only]
```

---

# 15. Natural Language Examples

## Basic

```text
"Route me to Gediminas Tower."
```

→

```text
route(
  destination = "Gediminas Tower",
  travel_mode = DEFAULT
)
```

---

## Explicit provider

```text
"Open Google Maps and route me to Gediminas Tower."
```

→

```text
route(
  destination = "Gediminas Tower",
  preferred_app = GOOGLE_MAPS
)
```

---

## Walking

```text
"Walking directions to Gediminas Tower."
```

→

```text
route(
  destination = "Gediminas Tower",
  travel_mode = WALKING
)
```

---

## Start navigation

```text
"Start navigating to Gediminas Tower."
```

→

```text
start(
  destination = "Gediminas Tower"
)
```

---

## Show only

```text
"Show Gediminas Tower on the map."
```

→

```text
show(
  destination = "Gediminas Tower"
)
```

---

## Avoid highways

```text
"Take me to Kaunas but avoid highways."
```

→

```text
route(
  destination = "Kaunas",
  travel_mode = DRIVING,
  avoid = { HIGHWAYS }
)
```

---

# 16. Capability Risk Classification

Navigation actions are generally low risk.

Suggested levels:

| Operation | Risk |
|---|---:|
| Search place | Level 0 |
| Resolve place | Level 0 |
| Show place | Level 1 |
| Show route | Level 1 |
| Start navigation | Level 1 |
| Change default navigation app | Level 2 |

No confirmation required by default for:

```text
search
show
route
start navigation
```

unless user policy says otherwise.

---

# 17. Privacy

Navigation queries may contain sensitive location information.

Rules:

- local resolution preferred where possible
- do not persist destination history unless enabled
- do not send current location to unrelated providers
- provider adapter should disclose when an online request is required
- offline provider option should exist
- AI audit log should store minimal navigation metadata by default

Example setting:

```text
Navigation history:
  [Do not save]
  [Save locally]
```

---

# 18. Current Location

The model should not directly read GPS.

Flow:

```text
AI
 ↓
lieppos.navigation.route
 ↓
Navigation Broker
 ↓
Location framework
 ↓
current location
```

The model can request:

```text
origin = CURRENT_LOCATION
```

The broker enforces location permissions.

---

# 19. Voice Integration

Example:

```text
User:
"Hey Liepp, take me to Gediminas Tower."
```

Pipeline:

```text
speech-to-text
      ↓
tiny router model
      ↓
navigation intent
      ↓
resolve place
      ↓
route/start
      ↓
Maps opens
```

This should not require loading the largest model.

A 1–2B router should handle navigation intents easily.

---

# 20. Model Routing

Navigation should normally stay in the cheapest inference path.

Example:

```text
"Take me to Gediminas Tower."
```

Use:

```text
tiny router
```

Not:

```text
4–8B reasoning model
```

Only escalate if the request needs reasoning:

```text
"Find a scenic route to Trakai with a charging stop and a place to eat."
```

Then use a larger planning model plus search/navigation tools.

---

# 21. Error Handling

Possible results:

```text
APP_NOT_INSTALLED
PLACE_NOT_FOUND
AMBIGUOUS_DESTINATION
ROUTE_PROVIDER_UNAVAILABLE
MODE_UNSUPPORTED
NO_LOCATION_PERMISSION
NO_NETWORK
OFFLINE_MAP_UNAVAILABLE
INVALID_DESTINATION
```

The LLM must receive structured errors.

Example:

```json
{
  "status": "APP_NOT_INSTALLED",
  "requested_provider": "GOOGLE_MAPS"
}
```

Then it can ask:

```text
"Google Maps is not installed. Use Organic Maps instead?"
```

---

# 22. No UI Automation by Default

Never default to:

```text
open app
tap search box
type text
tap destination
tap directions
```

Preferred:

```text
intent/deep link/API
```

UI automation is fragile because:

- layouts change
- translations change
- screen sizes differ
- popups appear
- accessibility state changes
- it is slower
- it consumes more battery
- it is harder to secure

UI automation should be a fallback capability with a higher risk level.

---

# 23. AppFunctions Integration

If a navigation provider later exposes Android AppFunctions, create an adapter:

```text
LieppOS navigation request
       ↓
Navigation Broker
       ↓
AppFunctionAdapter
       ↓
provider AppFunction
```

But the stable public AI API remains:

```text
lieppos.navigation.*
```

Do not make LieppOS dependent on a single provider's schema.

---

# 24. Initial Implementation

Phase 1:

Implement:

```text
lieppos.navigation.show
lieppos.navigation.route
lieppos.navigation.start
```

Adapters:

```text
Google Maps
default ACTION_VIEW handler
```

Support:

```text
DRIVING
WALKING
DEFAULT
```

Phase 1 success test:

```text
User:
"AI, make route via Maps to Gediminas Tower."

Expected:
Google Maps opens with Gediminas Castle Tower as destination
and the route screen visible.
```

No simulated typing.

---

# 25. Phase 2

Add:

```text
place search
ambiguity handling
current-location bias
Google place IDs / provider IDs
Organic Maps
OsmAnd
offline operation
transit
bicycling
avoid options
```

---

# 26. Phase 3

Add:

```text
multi-stop routes
saved places
contact-address navigation
calendar-location navigation
context-aware travel mode
traffic-aware provider support
```

Examples:

```text
"Navigate to my next meeting."
```

```text
"Take me to John's house."
```

```text
"Route me home after this appointment."
```

These require permissions from Calendar/Contacts but still use the same navigation broker.

---

# 27. Phase 4

AI-assisted trip planning:

```text
"Plan a route from Vilnius to Klaipėda,
stop somewhere good for lunch,
and keep the detour under 15 minutes."
```

Pipeline:

```text
planner model
   ↓
place/business search
   ↓
candidate stops
   ↓
navigation route API
   ↓
provider
```

The LLM performs planning.

The map provider performs navigation.

---

# 28. Proposed Source Layout

```text
packages/modules/LieppAI/navigation/
├── aidl/
│   └── ILieppNavigationService.aidl
├── broker/
│   └── NavigationBroker.*
├── model/
│   ├── Place.*
│   ├── RouteRequest.*
│   └── NavigationResult.*
├── providers/
│   ├── GoogleMapsAdapter.*
│   ├── DefaultMapsAdapter.*
│   ├── OrganicMapsAdapter.*
│   └── OsmAndAdapter.*
├── policy/
├── resolver/
└── tests/
```

---

# 29. Example AIDL

Concept only:

```aidl
interface ILieppNavigationService {
    NavigationResult showPlace(in PlaceRequest request);
    NavigationResult route(in RouteRequest request);
    NavigationResult startNavigation(in RouteRequest request);
}
```

Possible request:

```text
RouteRequest {
    destination
    origin
    travelMode
    preferredProvider
    avoidOptions
}
```

---

# 30. Testing

Mandatory tests:

## Intent parsing

```text
"Take me to Gediminas Tower"
"Route to Gediminas Tower"
"Walking route to Gediminas Tower"
"Open Google Maps to Gediminas Tower"
"Show Gediminas Tower"
```

## Ambiguity

```text
"Take me to Gediminas"
```

must not select an arbitrary destination when multiple plausible results exist.

## Provider

- Google Maps installed
- Google Maps absent
- default map provider only
- offline provider
- unsupported travel mode

## Security

- model cannot read raw GPS directly
- model cannot launch arbitrary intents through navigation tool
- URI parameters sanitized
- provider package allowlisted
- no shell invocation

## Privacy

- current location requires permission
- history policy respected
- offline provider does not accidentally contact Google

---

# 31. Final Goal

The user experience should be:

```text
User:
"AI, make route via Maps to Gediminas Tower."

LieppOS AI:
understands request
      ↓
resolves destination
      ↓
chooses preferred maps provider
      ↓
opens route directly
```

No manual typing.

No screen scraping.

No unrestricted automation.

The AI understands **intent**.

LieppOS performs **trusted action translation**.

The maps application performs **navigation**.
