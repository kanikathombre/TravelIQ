# TRAVELIQ — Travel Cost Methodology

## 1. Purpose

TRAVELIQ provides estimated travel costs to help users compare destinations
against their available budget.

The costs displayed by TRAVELIQ are estimates and should not be interpreted
as guaranteed booking prices.

Actual prices may vary depending on travel dates, season, availability,
booking time, accommodation category, transportation provider, and user
preferences.

---

## 2. Cost Components

TRAVELIQ separates travel cost into the following components:

### 2.1 Accommodation Cost

Estimated accommodation expenditure per person per day.

This represents a typical budget-to-mid-range travel style rather than
luxury accommodation.

---

### 2.2 Food Cost

Estimated daily food expenditure per person.

The estimate represents normal tourist spending on meals and excludes
premium restaurants and luxury dining.

---

### 2.3 Local Transport Cost

Estimated daily expenditure on transportation within the destination.

Examples include:

- Local buses
- Auto-rickshaws
- Taxis
- Metro/public transport
- Short-distance transfers

The value represents a typical tourist estimate rather than a live fare.

---

### 2.4 Activity Cost

Estimated daily expenditure on attractions and activities.

Examples include:

- Entry tickets
- Guided experiences
- Adventure activities
- Local attractions
- Tours

Free attractions may reduce the actual amount spent.

---

## 3. Average Daily Cost

TRAVELIQ calculates the estimated average daily destination cost as:

    avg_daily_cost =
        accommodation_cost
        + food_cost
        + transport_cost
        + activity_cost

This value represents the estimated daily spending at the destination.

It does not include transportation required to reach the destination.

---

## 4. Intercity Transportation

Transportation between the user's origin and destination is treated
separately from the destination's daily cost.

For example:

    Pune → Hampi

The estimated trip cost is:

    Origin-to-destination transport
    +
    Destination daily expenses

This prevents the destination's daily cost from depending on where the
traveller starts their journey.

---

## 5. Estimated Trip Cost

For a trip of N days:

    destination_cost =
        avg_daily_cost × trip_duration

The estimated total trip cost is:

    estimated_trip_cost =
        destination_cost
        + intercity_transport
        + visa_cost

where applicable.

For domestic Indian travel, visa cost is not applicable.

---

## 6. Cost Data Classification

Every cost value used by TRAVELIQ should be classified as one of:

### Estimated

A value derived from documented assumptions, averages, or aggregated
source information.

### API / Live

A value retrieved dynamically from an external API or live data provider.

### User Input

A value provided directly by the user.

TRAVELIQ should clearly communicate which type of value is being shown.

---

## 7. Data Quality Rules

TRAVELIQ must not:

- Present estimated costs as guaranteed prices.
- Claim that an estimate is a live booking price.
- Invent prices without documenting the methodology.
- Mix currencies without recording the currency.
- Hide major cost assumptions.
- Treat one specific hotel, flight, or booking as representative of
  an entire destination without qualification.

---

## 8. Currency

The destination dataset stores the local currency of each destination.

For Indian destinations:

    currency = INR

When international destinations are added, the original/local currency
will be retained in the dataset.

The frontend may convert the displayed estimate into the user's preferred
currency using a currency conversion source/API.

---

## 9. Future Improvements

The initial TRAVELIQ version will use estimated destination-level costs.

Future versions may incorporate:

- Live flight prices
- Live hotel prices
- Seasonal price adjustments
- Currency exchange rates
- User-selected accommodation category
- Budget / standard / premium travel styles
- Real-time activity pricing
- Historical price trends

These features should be introduced without changing the distinction
between estimated and live data.

---

## 10. Current Dataset Status

The following fields are part of the TRAVELIQ destination cost model:

- accommodation_cost
- food_cost
- transport_cost
- activity_cost
- avg_daily_cost

These fields will be populated only after the corresponding data sources
and estimation methodology have been documented.