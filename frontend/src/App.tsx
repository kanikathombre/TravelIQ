import { Link } from "react-router-dom";

import { useEffect, useState } from "react";

import { motion } from "framer-motion";

import {

  ArrowDownRight,

  ArrowUpRight,

  ArrowRight,

  Compass,

  Globe2,

  MapPin,

  Search,

  Sparkles,

  Wallet,

  CalendarDays,

  Users,

  Mountain,

  Waves,

  Leaf,

  Heart,

  LoaderCircle,

  AlertCircle,

} from "lucide-react";

import "./App.css";



const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";



type Destination = {

  destination_name: string;

  country: string;

  state_region: string;

  destination_type: string;

  latitude: number;

  longitude: number;

  best_months: string;

  recommended_stay_days: number | null;

  avg_daily_cost_inr: number | null;

  tourist_rating: number | null;

  cost_data_quality: string | null;

  adventure_score: number | null;

  beach_score: number | null;

  nature_score: number | null;

  culture_score: number | null;

  source: string | null;

};



type Recommendation = Destination & {

  overall_score: number | null;

  estimated_total_cost_inr: number | null;

  explanations: string[];

  data_warnings: string[];

};



const interests = [

  { name: "Nature", icon: Leaf },

  { name: "Adventure", icon: Mountain },

  { name: "Beaches", icon: Waves },

  { name: "Culture", icon: Globe2 },

  { name: "Romance", icon: Heart },

];



const images: Record<string, string> = {

  Hampi:

    "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=900&q=85",

  Mysuru:

    "https://images.unsplash.com/photo-1600112356915-089abb8fc71a?auto=format&fit=crop&w=900&q=85",

  Kumarakom:

    "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=900&q=85",

  Shillong:

    "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=85",

  Sohra:

    "https://images.unsplash.com/photo-1472396961693-142e6e269027?auto=format&fit=crop&w=900&q=85",

  Jodhpur:

    "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?auto=format&fit=crop&w=900&q=85",

  Gangtok:

    "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=900&q=85",

  Leh:

    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=900&q=85",

  Lakshadweep:

    "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=900&q=85",

  Puducherry:

    "https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?auto=format&fit=crop&w=900&q=85",

};



function photoFor(name: string) {

  return (

    images[name] ??

    "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=900&q=85"

  );

}



function money(value: number | null | undefined) {

  if (value == null || !Number.isFinite(value)) return "Not available";

  return `₹${Math.round(value).toLocaleString("en-IN")}`;

}



function App() {

  const [destinations, setDestinations] = useState<Destination[]>([]);

  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  const [budget, setBudget] = useState("2500");

  const [month, setMonth] = useState("12");

  const [duration, setDuration] = useState("3");

  const [traveler, setTraveler] = useState("friends");

  const [style, setStyle] = useState("budget");

  const [scope, setScope] = useState("india");

  const [interestsSelected, setInterestsSelected] = useState<string[]>([

    "nature",

    "adventure",

  ]);

  const [searchText, setSearchText] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [apiOnline, setApiOnline] = useState(false);



  useEffect(() => {

    fetch(`${API}/api/destinations`)

      .then((res) => {

        if (!res.ok) throw new Error("Could not load destinations");

        return res.json();

      })

      .then((data: Destination[]) => {

        setDestinations(data);

        setApiOnline(true);

      })

      .catch(() => {

        setApiOnline(false);

        setError(

          "We couldn't connect to the TravelIQ API. Make sure your backend is running on port 8000.",

        );

      });

  }, []);



  async function findTrips(event?: React.FormEvent) {

    event?.preventDefault();

    setLoading(true);

    setError("");



    try {

      const response = await fetch(`${API}/api/recommendations`, {

        method: "POST",

        headers: { "Content-Type": "application/json" },

        body: JSON.stringify({

          daily_budget_inr: Number(budget),

          travel_months: [Number(month)],

          trip_duration_days: Number(duration),

          interests: interestsSelected,

          traveler_type: traveler,

          travel_style: style,

          destination_scope: scope,

        }),

      });



      if (!response.ok) {

        const detail = await response.text();

        throw new Error(`Recommendation request failed: ${detail}`);

      }



      const data = await response.json();

      setRecommendations(data.results ?? []);



      window.setTimeout(() => {

        document

          .getElementById("recommendations")

          ?.scrollIntoView({ behavior: "smooth", block: "start" });

      }, 100);

    } catch (err) {

      setError(

        err instanceof Error ? err.message : "Something went wrong.",

      );

    } finally {

      setLoading(false);

    }

  }



  const visibleDestinations = destinations.filter((destination) => {

    const query = searchText.trim().toLowerCase();

    return (

      !query ||

      destination.destination_name.toLowerCase().includes(query) ||

      destination.state_region.toLowerCase().includes(query) ||

      destination.country.toLowerCase().includes(query)

    );

  });



  function toggleInterest(value: string) {

    setInterestsSelected((current) =>

      current.includes(value)

        ? current.filter((item) => item !== value)

        : [...current, value],

    );

  }



  return (

    <div className="travel-app">

      <header className="navbar">

        <a href="#home" className="brand">

          <span className="brand-icon">

            <Compass size={22} />

          </span>

          <span>travel<span className="brand-accent">IQ</span></span>

        </a>



        <nav className="nav-links">

          <a className="nav-active" href="#home">Discover</a>

          <a href="#destinations">Destinations</a>

          <a href="#planner">Trip planner</a>

          <a href="#insights">Insights</a>

        </nav>



        <a href="#planner" className="nav-cta">

          Plan a trip <ArrowRight size={16} />

        </a>

      </header>



      <main>

        <section className="hero" id="home">

          <div className="hero-image" />

          <div className="hero-overlay" />

          <div className="hero-content">

            <motion.div

              className="eyebrow hero-eyebrow"

              initial={{ opacity: 0, y: 12 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.5 }}

            >

              <Sparkles size={15} /> YOUR NEXT CHAPTER STARTS HERE

            </motion.div>



            <motion.h1

              initial={{ opacity: 0, y: 20 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.65, delay: 0.1 }}

            >

              The world is

              <br />

              <span>closer than</span> you think.

            </motion.h1>



            <motion.p

              initial={{ opacity: 0, y: 14 }}

              animate={{ opacity: 1, y: 0 }}

              transition={{ duration: 0.6, delay: 0.2 }}

            >

              Tell us your budget, your kind of adventure, and the time you

              have. We'll help you discover somewhere extraordinary.

            </motion.p>



            <div className="hero-actions">

              <a href="#planner" className="button button-lime">

                Find my destination <ArrowDownRight size={17} />

              </a>

              <a href="#destinations" className="text-link">

                Explore places <ArrowRight size={16} />

              </a>

            </div>



            <div className="hero-footnote">

              <span className={`status-dot ${apiOnline ? "" : "offline"}`} />

              {apiOnline

                ? `${destinations.length} destinations in your discovery database`

                : "Connecting to your discovery database"}

            </div>

          </div>



          <div className="hero-caption">

            <MapPin size={14} /> DISCOVER THE UNEXPECTED

          </div>

          <div className="hero-index">01 / DISCOVER</div>

        </section>



        <section className="intro-strip">

          <div>

            <span className="section-kicker">TRAVEL, REIMAGINED</span>

            <h2>

              Less scrolling.

              <br />

              <span>More discovering.</span>

            </h2>

          </div>

          <p>

            Great travel isn't just about where you go. It's about finding a

            place that fits your budget, your timing, and the way you want to

            feel.

          </p>

          <div className="intro-mark">

            <Globe2 size={42} strokeWidth={1} />

          </div>

        </section>



        <section className="planner-section" id="planner">

          <div className="section-heading">

            <div>

              <span className="section-kicker">YOUR TRIP, YOUR RULES</span>

              <h2>Where could you go?</h2>

            </div>

            <p>Make it yours. We'll do the matching.</p>

          </div>



          <form className="planner-card" onSubmit={findTrips}>

            <div className="form-grid">

              <label className="field">

                <span><Wallet size={15} /> DAILY BUDGET / PERSON</span>

                <div className="input-with-prefix">

                  <b>₹</b>

                  <input

                    type="number"

                    min="1"

                    value={budget}

                    onChange={(e) => setBudget(e.target.value)}

                    required

                  />

                </div>

              </label>



              <label className="field">

                <span><CalendarDays size={15} /> TRAVEL MONTH</span>

                <select value={month} onChange={(e) => setMonth(e.target.value)}>

                  {[

                    "January","February","March","April","May","June",

                    "July","August","September","October","November","December",

                  ].map((name, index) => (

                    <option value={index + 1} key={name}>{name}</option>

                  ))}

                </select>

              </label>



              <label className="field">

                <span><CalendarDays size={15} /> TRIP LENGTH</span>

                <select value={duration} onChange={(e) => setDuration(e.target.value)}>

                  {[1, 2, 3, 4, 5, 7, 10, 14].map((days) => (

                    <option value={days} key={days}>

                      {days} {days === 1 ? "day" : "days"}

                    </option>

                  ))}

                </select>

              </label>



              <label className="field">

                <span><Users size={15} /> WHO'S GOING?</span>

                <select value={traveler} onChange={(e) => setTraveler(e.target.value)}>

                  <option value="solo">Solo</option>

                  <option value="couple">Couple</option>

                  <option value="friends">Friends</option>

                  <option value="family">Family</option>

                </select>

              </label>



              <label className="field">

                <span><Wallet size={15} /> TRAVEL STYLE</span>

                <select value={style} onChange={(e) => setStyle(e.target.value)}>

                  <option value="budget">Budget</option>

                  <option value="standard">Standard</option>

                  <option value="premium">Premium</option>

                </select>

              </label>



              <label className="field">

                <span><Globe2 size={15} /> DESTINATION SCOPE</span>

                <select value={scope} onChange={(e) => setScope(e.target.value)}>

                  <option value="india">India</option>

                  <option value="international">International</option>

                  <option value="all">Anywhere</option>

                </select>

              </label>

            </div>



            <div className="interest-area">

              <span className="interest-label">WHAT ARE YOU IN THE MOOD FOR?</span>

              <div className="interest-options">

                {interests.map(({ name, icon: Icon }) => {

                  const key = name.toLowerCase().replace("beaches", "beach");

                  const selected = interestsSelected.includes(key);

                  return (

                    <button

                      type="button"

                      key={name}

                      className={`interest-chip ${selected ? "selected" : ""}`}

                      onClick={() => toggleInterest(key)}

                    >

                      <Icon size={15} /> {name}

                    </button>

                  );

                })}

              </div>

            </div>



            <div className="planner-bottom">

              <p>Personalized suggestions, with transparent match scores.</p>

              <button className="button button-lime search-button" type="submit" disabled={loading}>

                {loading ? (

                  <><LoaderCircle className="spin" size={17} /> Finding places...</>

                ) : (

                  <><Search size={17} /> Find my places <ArrowRight size={16} /></>

                )}

              </button>

            </div>

          </form>



          {error && (

            <div className="error-banner">

              <AlertCircle size={18} /> {error}

            </div>

          )}

        </section>



        <section className="recommendations-section" id="recommendations">

          <div className="section-heading">

            <div>

              <span className="section-kicker">MADE FOR YOUR KIND OF TRIP</span>

              <h2>{recommendations.length ? "Your possible next stops." : "A few places to spark your imagination."}</h2>

            </div>

            <span className="result-count">

              {recommendations.length

                ? `${recommendations.length} MATCHES`

                : `${destinations.length} PLACES`}

            </span>

          </div>



          {recommendations.length > 0 ? (

            <>

              <p className="results-note">

                Ranked using your preferences. Scores are algorithmic matches,

                not guarantees. Check each destination's data warnings and

                verify current prices before booking.

              </p>

              <div className="destination-grid">

                {recommendations.slice(0, 6).map((place, index) => (

                  <DestinationCard key={place.destination_name} place={place} rank={index + 1} />

                ))}

              </div>

            </>

          ) : (

            <div className="destination-grid">

              {destinations.slice(0, 6).map((place, index) => (

                <DestinationCard key={place.destination_name} place={place} rank={index + 1} />

              ))}

              {!destinations.length && (

                <div className="empty-state">

                  Your destinations will appear here once the API is connected.

                </div>

              )}

            </div>

          )}



          <div className="center-action">

            <button

              className="button button-outline"

              onClick={() => (recommendations.length ? setRecommendations([]) : findTrips())}

            >

              {recommendations.length ? "Back to discovery" : "Get personalized recommendations"}

              <ArrowRight size={16} />

            </button>

          </div>

        </section>



        <section className="destinations-section" id="destinations">

          <div className="section-heading">

            <div>

              <span className="section-kicker">YOUR NEXT PIN ON THE MAP</span>

              <h2>Find a place by name.</h2>

            </div>

            <span className="result-count">{visibleDestinations.length} PLACES</span>

          </div>



          <div className="destination-search">

            <Search size={18} />

            <input

              placeholder="Search destinations, states or countries..."

              value={searchText}

              onChange={(e) => setSearchText(e.target.value)}

            />

          </div>



          <div className="destination-grid">

            {visibleDestinations.slice(0, 8).map((place, index) => (

              <DestinationCard key={place.destination_name} place={place} rank={index + 1} />

            ))}

          </div>

        </section>



        <section className="insights-section" id="insights">

          <div>

            <span className="section-kicker">A LITTLE MORE CLARITY</span>

            <h2>Good trips start with good information.</h2>

            <p>

              TravelIQ combines destination attributes, estimated costs,

              seasonal guidance and an explainable recommendation engine.

              Missing data stays visible instead of being presented as fact.

            </p>

          </div>

          <div className="insight-stat">

            <strong>{destinations.length.toString().padStart(2, "0")}</strong>

            <span>DESTINATIONS IN THE CURRENT DATASET</span>

          </div>

          <div className="insight-stat">

            <strong>01</strong>

            <span>EXPLAINABLE RECOMMENDATION ENGINE</span>

          </div>

        </section>

      </main>



      <footer className="footer">

        <a href="#home" className="brand">

          <span className="brand-icon"><Compass size={20} /></span>

          <span>travel<span className="brand-accent">IQ</span></span>

        </a>

        <span>Go somewhere that feels like you.</span>

        <span className="footer-status">

          <span className={`status-dot ${apiOnline ? "" : "offline"}`} />

          {apiOnline ? "API connected" : "API disconnected"}

        </span>

      </footer>

    </div>

  );

}





function DestinationCard({

  place,

  index = 0,

  rank,

}: {

  place: {

    destination_name: string;

    country?: string;

    state_region?: string;

    destination_type?: string;

    best_months?: string;

    recommended_stay_days?: number | null;

    avg_daily_cost_inr?: number | null;

    avg_daily_cost?: number | null;

    latitude?: number;

    longitude?: number;

  };

  index?: number;

  rank?: number;

}) {

  const destinationUrl = `/destination/${encodeURIComponent(

    place.destination_name,

  )}`;



  const dailyCost =

    place.avg_daily_cost_inr ?? place.avg_daily_cost ?? null;



  const formattedCost = money(dailyCost);



  const location = [place.state_region, place.country]

    .filter(Boolean)

    .join(", ");



  return (

  <motion.article

    className="destination-card"

    initial={{ opacity: 0, y: 18 }}

    whileInView={{ opacity: 1, y: 0 }}

    viewport={{ once: true, amount: 0.15 }}

    transition={{

      duration: 0.4,

      delay: Math.min(index * 0.06, 0.3),

    }}

  >

    <Link

      to={destinationUrl}

      className="destination-card-link"

      aria-label={`View details for ${place.destination_name}`}

    >

      <div

        className="destination-card-image"

        style={{

          backgroundImage: `url("${photoFor(place.destination_name)}")`,

          backgroundSize: "cover",

          backgroundPosition: "center",

        }}

      >

        <img

          src={photoFor(place.destination_name)}

          alt={`${place.destination_name}, ${location || "travel destination"}`}

          loading="lazy"

          onError={(event) => {
            const image = event.currentTarget;
            if (image.dataset.fallbackApplied === "true") {
              image.style.display = "none";
              return;
            }
            image.dataset.fallbackApplied = "true";
            image.src = "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=900&q=85";
          }}

        />



        <div className="destination-card-number">

          {String(rank ?? index + 1).padStart(2, "0")}

        </div>



        <div className="destination-card-image-action">

          <ArrowUpRight size={19} />

        </div>

      </div>



      <div className="destination-card-body">

        <p className="destination-card-location">

          <MapPin size={14} />

          {location || "Location not specified"}

        </p>



        <h3>{place.destination_name}</h3>



        <p className="destination-card-type">

          {place.destination_type || "Destination"}

        </p>



        <div className="destination-card-stats">

          <div>

            <span>FROM / DAY</span>

            <strong>{formattedCost}</strong>

          </div>



          <div>

            <span>IDEAL STAY</span>

            <strong>

              {place.recommended_stay_days

                ? `${place.recommended_stay_days} days`

                : "Not specified"}

            </strong>

          </div>

        </div>



        <p className="destination-card-season">

          <CalendarDays size={14} />

          Best months: {place.best_months || "Not specified"}

        </p>



        <span className="destination-card-view">

          Explore destination <ArrowUpRight size={14} />

        </span>

      </div>

    </Link>

  </motion.article>

);

}





export default App;
