

import { useEffect, useState } from "react";

import { Link, useParams } from "react-router-dom";

import {

  ArrowLeft,

  CalendarDays,

  MapPin,

  Wallet,

  Clock,

  AlertCircle,

  ExternalLink,

} from "lucide-react";

import {

  MapContainer,

  Marker,

  Popup,

  TileLayer,

} from "react-leaflet";

import "leaflet/dist/leaflet.css";



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

  accommodation_cost: number | null;

  food_cost: number | null;

  transport_cost: number | null;

  activity_cost: number | null;

  currency: string;

  cost_data_quality: string | null;

  tourist_rating: number | null;

  safety_score: number | null;

  source: string | null;

};



const photos: Record<string, string> = {

  Hampi: "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=1800&q=90",

  Mysuru: "https://images.unsplash.com/photo-1600112356915-089abb8fc71a?auto=format&fit=crop&w=1800&q=90",

  Kumarakom: "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=1800&q=90",

  Shillong: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1800&q=90",

  Sohra: "https://images.unsplash.com/photo-1472396961693-142e6e269027?auto=format&fit=crop&w=1800&q=90",

  Jodhpur: "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?auto=format&fit=crop&w=1800&q=90",

  Gangtok: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1800&q=90",

  Leh: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1800&q=90",

};



function formatMoney(value: number | null | undefined) {

  if (value == null || !Number.isFinite(value)) return "Unavailable";

  return `₹${Math.round(value).toLocaleString("en-IN")}`;

}



function MapView({ destination }: { destination: Destination }) {

  const position: [number, number] = [

    destination.latitude,

    destination.longitude,

  ];



  return (

    <MapContainer

      center={position}

      zoom={10}

      scrollWheelZoom={false}

      style={{ height: "390px", width: "100%" }}

      className="destination-leaflet-map"

    >

      <TileLayer

        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

        attribution='&copy; OpenStreetMap contributors'

      />

      <Marker position={position}>

        <Popup>{destination.destination_name}</Popup>

      </Marker>

    </MapContainer>

  );

}



export default function DestinationDetails() {

  const { name } = useParams<{ name: string }>();

  const [destination, setDestination] = useState<Destination | null>(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");



  useEffect(() => {

    if (!name) {

      setError("No destination was specified.");

      setLoading(false);

      return;

    }



    const controller = new AbortController();



    async function loadDestination() {

      try {

        setLoading(true);

        setError("");



        const response = await fetch(

          `${API}/api/destinations/${encodeURIComponent(name!)}`,

          { signal: controller.signal },

        );



        if (!response.ok) {

          throw new Error(

            response.status === 404

              ? "We couldn't find that destination."

              : "Unable to load destination details.",

          );

        }



        const data: Destination = await response.json();

        setDestination(data);

      } catch (err) {

        if (err instanceof Error && err.name === "AbortError") return;

        setError(

          err instanceof Error

            ? err.message

            : "Something went wrong loading this destination.",

        );

      } finally {

        if (!controller.signal.aborted) setLoading(false);

      }

    }



    loadDestination();

    return () => controller.abort();

  }, [name]);



  if (loading) {

    return (

      <main className="detail-status">

        <p>Loading destination details...</p>

      </main>

    );

  }



  if (error || !destination) {

    return (

      <main className="detail-status">

        <AlertCircle size={24} />

        <h1>Destination unavailable</h1>

        <p>{error || "We couldn't load this destination."}</p>

        <Link className="button button-lime" to="/">

          <ArrowLeft size={16} /> Back to TravelIQ

        </Link>

      </main>

    );

  }



  const image =

    photos[destination.destination_name] ??

    "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=1800&q=90";



  const costs = [

    ["Accommodation", destination.accommodation_cost],

    ["Food", destination.food_cost],

    ["Local transport", destination.transport_cost],

    ["Activities", destination.activity_cost],

  ] as const;



  return (

    <main className="detail-page">

      <section

        className="detail-hero"

        style={{ backgroundImage: `url("${image}")` }}

      >

        <div className="detail-hero-overlay" />

        <div className="detail-hero-content">

          <Link to="/" className="detail-back">

            <ArrowLeft size={16} /> Back to discovery

          </Link>

          <div className="section-kicker">YOUR NEXT ADVENTURE</div>

          <h1>{destination.destination_name}</h1>

          <p className="detail-location">

            <MapPin size={17} />

            {destination.state_region}, {destination.country}

          </p>

          <span className="detail-type">{destination.destination_type}</span>

        </div>

      </section>



      <div className="detail-content">

        <section className="detail-facts">

          <div className="detail-fact">

            <CalendarDays size={20} />

            <span>BEST MONTHS</span>

            <strong>{destination.best_months || "Not specified"}</strong>

          </div>

          <div className="detail-fact">

            <Clock size={20} />

            <span>RECOMMENDED STAY</span>

            <strong>

              {destination.recommended_stay_days

                ? `${destination.recommended_stay_days} days`

                : "Not specified"}

            </strong>

          </div>

          <div className="detail-fact">

            <Wallet size={20} />

            <span>ESTIMATED DAILY COST</span>

            <strong>{formatMoney(destination.avg_daily_cost_inr)}</strong>

          </div>

        </section>



        <section className="detail-section">

          <div>

            <span className="section-kicker">PLAN WITH CLARITY</span>

            <h2>Know before you go.</h2>

            <p className="detail-description">

              Explore the destination's location and review its available cost

              estimates. These figures are indicative, not live booking prices.

              Check current travel conditions and prices before making plans.

            </p>

          </div>

          <div className="detail-map">

            <MapView destination={destination} />

          </div>

          <p className="map-caption">

            <MapPin size={14} /> {destination.latitude.toFixed(4)},{" "}

            {destination.longitude.toFixed(4)}

            {" · "}

            <a

              href={`https://www.openstreetmap.org/?mlat=${destination.latitude}&mlon=${destination.longitude}#map=10/${destination.latitude}/${destination.longitude}`}

              target="_blank"

              rel="noreferrer"

            >

              View on OpenStreetMap <ExternalLink size={12} />

            </a>

          </p>

        </section>



        <section className="detail-section">

          <span className="section-kicker">COST BREAKDOWN</span>

          <h2>Understand your budget.</h2>

          <p className="detail-description">

            Estimated costs per person per day, in {destination.currency || "INR"}.

          </p>

          <div className="cost-list">

            {costs.map(([label, value]) => (

              <div className="cost-row" key={label}>

                <span>{label}</span>

                <strong>{formatMoney(value)}</strong>

              </div>

            ))}

            <div className="cost-row cost-total">

              <span>Estimated daily total</span>

              <strong>{formatMoney(destination.avg_daily_cost_inr)}</strong>

            </div>

          </div>

          <p className="cost-quality">

            Data quality: {destination.cost_data_quality || "Not specified"}.

            Accommodation assumptions and the actual prices you pay may vary.

          </p>

        </section>



        <section className="detail-section detail-data">

          <span className="section-kicker">TRANSPARENCY MATTERS</span>

          <h2>What we know—and what we don't.</h2>

          <div className="detail-data-grid">

            <div>

              <span>Tourist rating</span>

              <strong>

                {destination.tourist_rating ?? "Not available"}

              </strong>

            </div>

            <div>

              <span>Safety score</span>

              <strong>

                {destination.safety_score ?? "Not available"}

              </strong>

            </div>

            <div>

              <span>Data source</span>

              <strong>{destination.source || "Not specified"}</strong>

            </div>

          </div>

          <p className="detail-description">

            Missing scores are not treated as zero or as a guarantee. Confirm

            current safety advisories and local conditions before travelling.

          </p>

        </section>



        <div className="detail-footer-action">

          <Link className="button button-lime" to="/#planner">

            Find your next destination <ArrowLeft size={16} />

          </Link>

        </div>

      </div>

    </main>

  );

}
