import React, { useState, useEffect, useRef } from 'react';

import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Snackbar,
  Alert,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import useGeoLocation from '../hooks/useGeoLocation';
import { getNearbyAttractions } from '../services/api';

/* ── Fonts ───────────────────────────────────────────────────────── */
const FontLink = () => {
  useEffect(() => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500;600&display=swap";
    document.head.appendChild(link);
  }, []);
  return null;
};

/* ── DATA ────────────────────────────────────────────────────────── */
const SLIDES = [
  { label: "Spices of the Medina",  sub: "Rahba Kedima · Marrakech" },
  { label: "Leather & Babouches",   sub: "Souk Smata · Marrakech" },
  { label: "Brass Lanterns",        sub: "Souk Haddadine · Marrakech" },
  { label: "Argan & Botanicals",    sub: "Souk El Attarine · Marrakech" },
  { label: "Berber Carpets",        sub: "Souk Zrabi · Marrakech" },
  { label: "Silver Jewelry",        sub: "Souk des Bijoutiers · Marrakech" },
  { label: "Ceramics & Tagines",    sub: "Souk Semmarine · Marrakech" },
];
const SLIDE_BG = [
  "linear-gradient(160deg,#c4a882,#8b6542,#5c3e20)",
  "linear-gradient(160deg,#b5451b,#7a2d10,#3d1608)",
  "linear-gradient(160deg,#8c7355,#5c4a30,#3d3020)",
  "linear-gradient(160deg,#6b9c6b,#4a7a4a,#2d5c2d)",
  "linear-gradient(160deg,#c8a870,#8c6830,#5c4210)",
  "linear-gradient(160deg,#7a8c9c,#4a6070,#2d4050)",
  "linear-gradient(160deg,#c4956a,#8b5e38,#5c3c1e)",
];
const SLIDE_EMOJI = ["🌶️","👟","🏮","🍶","🧺","🪬","🏺"];

/* ── EXACT menu items from Mason & Fifth screenshot ── */
const MENU_NAV  = ["Our Products","Offers","Price Detection","Souk Guide","Events","About Us","Our Story"];
const MENU_FOOT = ["Contact","FAQ","Instagram","Privacy policy"];

const CATEGORIES = ["All Categories","Spices","Leather","Textiles","Ceramics","Lanterns","Jewelry","Argan Oil"];
const SOUKS_LIST = ["All Souks","Souk Semmarine","Souk Smata","Souk Zrabi","Rahba Kedima","Souk Haddadine","Souk des Bijoutiers","Souk El Attarine"];
const BUDGETS    = ["Any Budget","Under 50 MAD","50–200 MAD","200–500 MAD","500–1,000 MAD","1,000+ MAD"];

const PRICES = [
  { cat:"Leather",  name:"Babouches",       arabic:"بلغة",        souk:"Souk Smata",       range:"80–150 MAD",     note:"Traditional pointed-toe leather. Rises with embroidery." },
  { cat:"Spices",   name:"Spices & Herbs",   arabic:"بهارات",       souk:"Rahba Kedima",     range:"30–80 MAD/100g", note:"Cumin, saffron, ras el hanout. Weighed fresh." },
  { cat:"Argan",    name:"Argan Oil",         arabic:"زيت أركان",    souk:"Souk El Attarine", range:"150–300 MAD",    note:"Real oil = thick paste + strong nut aroma." },
  { cat:"Crafts",   name:"Tagine Pot",        arabic:"طاجين",        souk:"Souk Semmarine",   range:"20–50 MAD",      note:"Decorative or functional. Clay, hand-painted." },
  { cat:"Lanterns", name:"Moroccan Lantern",  arabic:"فانوس مغربي",  souk:"Souk Haddadine",   range:"100–800 MAD",    note:"Metal and glass. Stunning shadows when lit." },
  { cat:"Textiles", name:"Berber Carpet",     arabic:"زربية بربرية", souk:"Souk Zrabi",       range:"800–5,000+ MAD", note:"Beni Ourain rugs. Shipping available." },
];
const STEPS = [
  { num:"01", icon:"📷", title:"Capture",  desc:"Photograph any price tag or product in the souk with your phone." },
  { num:"02", icon:"🔍", title:"Detect",   desc:"Computer vision locates the price region on busy market stalls." },
  { num:"03", icon:"🧠", title:"Extract",  desc:"OCR reads prices in MAD — handwritten tags, Arabic numerals." },
  { num:"04", icon:"✅", title:"Compare",  desc:"Instantly checked against our 2025/2026 fair price database." },
];
const SOUKS_DIR = [
  { name:"Souk Semmarine",     spec:"Bags, shoes, pottery, fabrics" },
  { name:"Souk Smata",         spec:"Babouches & leather slippers" },
  { name:"Souk Zrabi",         spec:"Handmade carpets & rugs" },
  { name:"Souk Cherratine",    spec:"Leather bags, belts, wallets" },
  { name:"Rahba Kedima",       spec:"Spices, herbs, rosewater" },
  { name:"Souk Haddadine",     spec:"Blacksmiths & brass lanterns" },
  { name:"Souk des Bijoutiers",spec:"Silver & Berber jewelry" },
  { name:"Souk Chouari",       spec:"Wood, baskets, games" },
  { name:"Souk El Attarine",   spec:"Argan oil & perfumes" },
];
const CAT_COLORS = { Leather:"#8B4513",Spices:"#e67e22",Argan:"#16a085",Crafts:"#27ae60",Lanterns:"#f39c12",Textiles:"#8e44ad" };

/* ── scroll reveal ───────────────────────────────────────────────── */
function useReveal() {
  const ref = useRef(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVis(true); }, { threshold: 0.1 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  return [ref, vis];
}
function Reveal({ children, delay = 0 }) {
  const [ref, vis] = useReveal();
  return (
    <div ref={ref} style={{ opacity: vis ? 1 : 0, transform: vis ? "translateY(0)" : "translateY(26px)", transition: `opacity .7s ease ${delay}s, transform .7s ease ${delay}s` }}>
      {children}
    </div>
  );
}

/* ── Subscribe modal ─────────────────────────────────────────────── */
function SubscribeModal({ onClose }) {
  const [email, setEmail] = useState("");
  const [done, setDone] = useState(false);
  return (
    <div style={{ position:"fixed", top:62, right:14, zIndex:600, width:318, background:"#c3cfd8", borderRadius:10, boxShadow:"0 16px 56px rgba(0,0,0,0.22)", overflow:"hidden" }}>
      <button onClick={onClose} style={{ position:"absolute", top:13, right:13, background:"none", border:"none", fontSize:"0.95rem", cursor:"pointer", color:"#1C1A17" }}>✕</button>
      <div style={{ padding:"26px 26px 8px" }}><div style={{ fontSize:"3.6rem", lineHeight:1 }}>🦅</div></div>
      <div style={{ padding:"8px 26px 26px" }}>
        {done
          ? <p style={{ fontFamily:"'Cormorant Garamond',serif", fontSize:"1.1rem", fontStyle:"italic", color:"#1C1A17" }}>You're in! We'll be in touch.</p>
          : <>
              <p style={{ fontSize:"0.85rem", fontWeight:500, color:"#1C1A17", marginBottom:13, lineHeight:1.5 }}>Receive 10% off on your first price detection!</p>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Enter your email address"
                style={{ width:"100%", boxSizing:"border-box", background:"rgba(255,255,255,0.75)", border:"1.5px solid rgba(255,255,255,0.95)", borderRadius:5, padding:"11px 13px", fontFamily:"'Jost',sans-serif", fontSize:"0.82rem", outline:"none", color:"#1C1A17", marginBottom:9 }} />
              <button onClick={() => email && setDone(true)} style={{ width:"100%", background:"#1C1A17", color:"white", border:"none", borderRadius:5, padding:11, fontFamily:"'Jost',sans-serif", fontSize:"0.74rem", letterSpacing:"0.09em", textTransform:"uppercase", cursor:"pointer", marginBottom:13 }}>Subscribe</button>
              <p style={{ fontSize:"0.73rem", color:"#3a3530", lineHeight:1.65 }}><strong>We promise we'll never spam.</strong> You'll only hear from us when we have something worth sharing.</p>
            </>
        }
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   MENU PANEL — exact Mason & Fifth layout from screenshot:
   ┌─────────────────────────────────┐
   │ Souk&Price              [✕]     │  ← top bar, same bg as panel
   │                                 │
   │        Our Buildings            │
   │           Offers                │  ← large serif, centred,
   │      Meadow Workspace           │    vertically centred in
   │      Canal Restaurant           │    remaining space
   │          Events                 │
   │        Spirit Level             │
   │         Our Story               │
   │                                 │
   │  Contact, FAQ, Instagram, ...   │  ← small footer links
   ├─────────────────────────────────┤
   │ Book a stay │ Check-In │ Check-Out│  ← booking bar, white bg
   └─────────────────────────────────┘
   • Panel width  : ~490px
   • Panel bg     : #EDEAE3 (warm grey, matches M&F)
   • Slides in from left with CSS transform
   • Blurred semi-transparent backdrop behind it
   • Clicking backdrop closes panel
   • Booking bar is INSIDE panel, pinned to bottom
   ══════════════════════════════════════════════════════════════════ */
function MenuPanel({ onClose, category, setCategory, souk, setSouk, budget, setBudget }) {
  /* Two-frame trick: mount → next frame → set entered=true → CSS transition runs */
  const [entered, setEntered] = useState(false);
  useEffect(() => {
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setEntered(true)));
    return () => cancelAnimationFrame(id);
  }, []);

  /* Close with slide-out animation */
  const handleClose = () => {
    setEntered(false);
    setTimeout(onClose, 380); // match transition duration
  };

  const sel = {
    background:"none", border:"none", fontFamily:"'Jost',sans-serif",
    fontSize:"0.75rem", color:"#888", outline:"none", cursor:"pointer",
    width:"100%", padding:0, appearance:"none", WebkitAppearance:"none",
  };

  return (
    <>
      {/* ── Backdrop: blurs + dims page behind the panel ── */}
      <div
        onClick={handleClose}
        style={{
          position: "fixed", inset: 0, zIndex: 290,
          backdropFilter: "blur(3px)",
          WebkitBackdropFilter: "blur(3px)",
          background: "rgba(0,0,0,0.12)",
          opacity: entered ? 1 : 0,
          transition: "opacity 0.38s ease",
        }}
      />

      {/* ── Panel ── */}
      <div style={{
        position: "fixed",
        top: 0, left: 0, bottom: 0,
        zIndex: 300,
        width: 490,
        background: "#EDEAE3",           /* warm grey, matches screenshot */
        display: "flex",
        flexDirection: "column",
        transform: entered ? "translateX(0)" : "translateX(-100%)",
        transition: "transform 0.38s cubic-bezier(0.4, 0, 0.2, 1)",
        boxShadow: "6px 0 48px rgba(0,0,0,0.13)",
        /* No border-radius on right — matches M&F (panel reaches screen edge) */
      }}>

        {/* ── Row 1: Logo text  +  ✕ button ── */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "18px 20px",
          flexShrink: 0,
        }}>
          {/* Logo — plain text, same style as header pill but without the white bg */}
          <span style={{
            fontFamily: "'Jost',sans-serif",
            fontWeight: 700,
            fontSize: "1rem",
            letterSpacing: "-0.01em",
            color: "#1C1A17",
          }}>
            Souk&amp;Price
          </span>

          {/* ✕ — square button with border, exactly like M&F screenshot */}
          <button
            onClick={handleClose}
            style={{
              width: 38, height: 38,
              background: "transparent",
              border: "1.5px solid rgba(28,26,23,0.22)",
              borderRadius: 7,
              display: "flex", alignItems: "center", justifyContent: "center",
              cursor: "pointer",
              fontSize: "0.88rem",
              color: "#1C1A17",
              flexShrink: 0,
              transition: "background 0.2s",
            }}
            onMouseOver={e => e.currentTarget.style.background = "rgba(28,26,23,0.06)"}
            onMouseOut={e => e.currentTarget.style.background = "transparent"}
          >
            ✕
          </button>
        </div>

        {/* ── Nav links: vertically centred, large serif, centred text ── */}
        <nav style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",   /* vertical centre — key M&F detail */
          padding: "8px 32px 8px",
          gap: 0,
          overflow: "hidden",
        }}>
          {MENU_NAV.map((item, i) => (
            <a
              key={item}
              href="#"
              onClick={handleClose}
              style={{
                display: "block",
                width: "100%",
                textAlign: "center",
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontSize: "2.15rem",    /* large serif — matches screenshot */
                fontWeight: 400,
                lineHeight: 1.45,
                color: "#1C1A17",
                textDecoration: "none",
                /* staggered fade-up on enter */
                opacity: entered ? 1 : 0,
                transform: entered ? "translateY(0)" : "translateY(10px)",
                transition: `opacity 0.42s ease ${i * 0.05 + 0.08}s,
                             transform 0.42s ease ${i * 0.05 + 0.08}s,
                             color 0.2s`,
              }}
              onMouseOver={e => e.currentTarget.style.color = "#B5451B"}
              onMouseOut={e => e.currentTarget.style.color = "#1C1A17"}
            >
              {item}
            </a>
          ))}
        </nav>

        {/* ── Footer links: Contact, FAQ, Instagram, Privacy policy ── */}
        <div style={{
          padding: "0 24px 14px",
          textAlign: "center",
          flexShrink: 0,
          opacity: entered ? 1 : 0,
          transition: "opacity 0.5s ease 0.45s",
        }}>
          <p style={{ fontSize: "0.74rem", color: "#9c9890", lineHeight: 2 }}>
            {MENU_FOOT.map((link, i) => (
              <span key={link}>
                <a
                  href="#"
                  onClick={handleClose}
                  style={{ color: "#9c9890", textDecoration: "none", transition: "color 0.2s" }}
                  onMouseOver={e => e.currentTarget.style.color = "#1C1A17"}
                  onMouseOut={e => e.currentTarget.style.color = "#9c9890"}
                >
                  {link}
                </a>
                {i < MENU_FOOT.length - 1 && <span style={{ margin: "0 4px" }}>,</span>}
              </span>
            ))}
          </p>
        </div>

        {/* ── Booking bar — white, pinned to very bottom of panel ── */}
        {/* Matches M&F: "Book a stay / All Locations | Check-In Select Dates | Check-Out Select Dates" */}
        <div style={{
          display: "flex",
          alignItems: "stretch",
          background: "white",
          borderTop: "1px solid rgba(28,26,23,0.09)",
          height: 68,
          flexShrink: 0,
        }}>
          {/* Book a stay */}
          <div style={{ flex: 1.4, padding: "10px 18px", borderRight: "1px solid #EBEBEB", display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <p style={{ fontSize: "0.71rem", fontWeight: 600, color: "#1C1A17", marginBottom: 3 }}>Book a stay</p>
            <select value={category} onChange={e => setCategory(e.target.value)} style={sel}>
              {CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>

          {/* Check-In */}
          <div style={{ flex: 1, padding: "10px 16px", borderRight: "1px solid #EBEBEB", display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <p style={{ fontSize: "0.71rem", fontWeight: 600, color: "#1C1A17", marginBottom: 3 }}>Check-In</p>
            <select value={souk} onChange={e => setSouk(e.target.value)} style={sel}>
              {SOUKS_LIST.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>

          {/* Check-Out */}
          <div style={{ flex: 1, padding: "10px 16px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
            <p style={{ fontSize: "0.71rem", fontWeight: 600, color: "#1C1A17", marginBottom: 3 }}>Check-Out</p>
            <select value={budget} onChange={e => setBudget(e.target.value)} style={sel}>
              {BUDGETS.map(b => <option key={b}>{b}</option>)}
            </select>
          </div>
        </div>

      </div>

      {/* Keyframes for nav link stagger */}
      <style>{`
        @keyframes menuLinkIn {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </>
  );
}

/* ── PriceCard ───────────────────────────────────────────────────── */
function PriceCard({ p, delay }) {
  const [hov, setHov] = useState(false);
  return (
    <Reveal delay={delay}>
      <div onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}
        style={{ background: hov ? "#fff" : "#FAF7F2", padding: "32px 28px", borderRight: "1px solid rgba(28,26,23,0.08)", transition: "background .3s", height: "100%" }}>
        <p style={{ fontSize: "0.62rem", letterSpacing: "0.15em", textTransform: "uppercase", color: CAT_COLORS[p.cat] || "#B5451B", marginBottom: 8 }}>{p.cat}</p>
        <h3 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.4rem", fontWeight: 400, marginBottom: 4, lineHeight: 1.2 }}>{p.name}</h3>
        <span style={{ display: "block", direction: "rtl", color: "#5C5549", fontSize: "0.82rem", fontStyle: "italic", fontFamily: "'Cormorant Garamond',serif", marginBottom: 14 }}>{p.arabic}</span>
        <p style={{ fontSize: "0.72rem", color: "#5C5549", marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ display: "inline-block", width: 12, height: 1, background: "#B5451B" }} />{p.souk}
        </p>
        <span style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "2rem", fontWeight: 300 }}>{p.range}</span>
        <p style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid rgba(28,26,23,0.08)", fontSize: "0.77rem", color: "#5C5549", lineHeight: 1.65 }}>{p.note}</p>
      </div>
    </Reveal>
  );
}

/* ── StepCard ────────────────────────────────────────────────────── */
function StepCard({ s, delay }) {
  const [hov, setHov] = useState(false);
  return (
    <Reveal delay={delay}>
      <div onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}
        style={{ background: hov ? "#26231f" : "#1C1A17", padding: "44px 32px", borderRight: "1px solid rgba(255,255,255,0.06)", transition: "background .3s", height: "100%" }}>
        <div style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "3rem", fontWeight: 300, color: "rgba(181,69,27,0.2)", marginBottom: 22 }}>{s.num}</div>
        <div style={{ width: 44, height: 44, background: "rgba(181,69,27,0.14)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.2rem", marginBottom: 20 }}>{s.icon}</div>
        <h4 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.3rem", fontWeight: 400, color: "white", marginBottom: 10 }}>{s.title}</h4>
        <p style={{ fontSize: "0.83rem", color: "#9d9080", lineHeight: 1.75, fontWeight: 300 }}>{s.desc}</p>
      </div>
    </Reveal>
  );
}

/* ── Newsletter ──────────────────────────────────────────────────── */
function Newsletter() {
  const [email, setEmail] = useState("");
  const [done, setDone] = useState(false);
  return (
    <div style={{ background: "#B5451B", padding: "90px 80px", textAlign: "center" }}>
      <Reveal><h2 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(2.2rem,4vw,3.8rem)", fontWeight: 300, color: "white", lineHeight: 1.1, marginBottom: 14 }}>Shop Marrakech with <em style={{ fontStyle: "italic" }}>confidence.</em></h2></Reveal>
      <Reveal delay={0.1}><p style={{ color: "rgba(255,255,255,0.75)", fontSize: "0.93rem", fontWeight: 300, marginBottom: 44 }}>Get price alerts and souk guides delivered to your inbox.</p></Reveal>
      <Reveal delay={0.2}>
        {done ? <p style={{ color: "white", fontFamily: "'Cormorant Garamond',serif", fontSize: "1.4rem", fontStyle: "italic" }}>✓ You're in!</p> : (
          <div style={{ display: "flex", maxWidth: 460, margin: "0 auto" }}>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="Your email address"
              style={{ flex: 1, background: "rgba(255,255,255,0.15)", border: "1px solid rgba(255,255,255,0.3)", borderRight: "none", padding: "15px 20px", color: "white", fontFamily: "'Jost',sans-serif", fontSize: "0.88rem", outline: "none", borderRadius: "2px 0 0 2px" }} />
            <button onClick={() => email && setDone(true)} style={{ background: "white", color: "#B5451B", border: "none", padding: "15px 26px", fontFamily: "'Jost',sans-serif", fontSize: "0.72rem", letterSpacing: "0.1em", textTransform: "uppercase", cursor: "pointer", fontWeight: 500, borderRadius: "0 2px 2px 0" }}>Subscribe</button>
          </div>
        )}
      </Reveal>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════════
   MAIN
   ════════════════════════════════════════════════════════════════════ */
export default function SoukPrice() {
  const navigate = useNavigate();
  const [showSubscribe, setShowSubscribe] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [slide, setSlide] = useState(0);
  const [category, setCategory] = useState("All Categories");
  const [souk, setSouk] = useState("All Souks");
  const [budget, setBudget] = useState("Any Budget");
  const [heroLoaded, setHeroLoaded] = useState(false);

  const { location, error, loading, getLocation } = useGeoLocation();
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [attractions, setAttractions] = useState([]);

  useEffect(() => {
    const t = setTimeout(() => setHeroLoaded(true), 80);
    const iv = setInterval(() => setSlide(s => (s + 1) % SLIDES.length), 5000);
    return () => { clearTimeout(t); clearInterval(iv); };
  }, []);

  useEffect(() => {
    if (location) {
      const fetchAttractions = async () => {
        try {
          const { data } = await getNearbyAttractions(location.latitude, location.longitude);
          setAttractions(data);
        } catch (err) {
          console.error('Failed to fetch nearby attractions:', err);
        }
      };
      fetchAttractions();
    }
  }, [location]);

  const handleDiscoverNearby = () => { getLocation(); };

  useEffect(() => {
    if (error) setSnackbarOpen(true);
  }, [error]);

  const ha = (d = 0) => ({
    opacity: heroLoaded ? 1 : 0,
    transform: heroLoaded ? "translateY(0)" : "translateY(18px)",
    transition: `opacity .7s ease ${d}s, transform .7s ease ${d}s`,
  });

  const sel = {
    background: "none", border: "none", fontFamily: "'Jost',sans-serif",
    fontSize: "0.76rem", color: "#888", outline: "none", cursor: "pointer",
    width: "100%", padding: 0, appearance: "none", WebkitAppearance: "none",
  };

  return (
    <div style={{ fontFamily: "'Jost',sans-serif", background: "#F5F0E8", color: "#1C1A17", overflowX: "hidden" }}>
      <FontLink />

      {/* ══════════════════════════════════════════════════════
          HEADER
          ══════════════════════════════════════════════════════ */}
      <header style={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 200 }}>

        {/* Top row: logo+burger | enquiries+subscribe */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 16px", background: "rgba(245,240,232,0.96)", backdropFilter: "blur(12px)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            {/* Logo pill */}
            <div style={{ background: "white", borderRadius: 8, padding: "9px 18px", boxShadow: "0 1px 6px rgba(0,0,0,0.07)" }}>
              <span style={{ fontFamily: "'Jost',sans-serif", fontWeight: 700, fontSize: "0.98rem", letterSpacing: "-0.01em", color: "#1C1A17" }}>Souk&amp;Price</span>
            </div>
            {/* Hamburger — 3 lines */}
            <button
              onClick={() => setShowMenu(m => !m)}
              style={{ background: "white", border: "none", borderRadius: 8, width: 42, height: 42, cursor: "pointer", boxShadow: "0 1px 6px rgba(0,0,0,0.07)", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 4.5 }}>
              <span style={{ display: "block", width: 17, height: 1.5, background: "#1C1A17", borderRadius: 2 }} />
              <span style={{ display: "block", width: 17, height: 1.5, background: "#1C1A17", borderRadius: 2 }} />
              <span style={{ display: "block", width: 17, height: 1.5, background: "#1C1A17", borderRadius: 2 }} />
            </button>
          </div>

          {/* Enquiries + Subscribe */}
          <div style={{ display: "flex", gap: 8 }}>
            {["Enquiries", "Subscribe"].map(label => (
              <button key={label}
                onClick={label === "Subscribe" ? () => setShowSubscribe(s => !s) : undefined}
                style={{ background: "white", color: "#1C1A17", border: "none", borderRadius: 22, padding: "9px 20px", fontFamily: "'Jost',sans-serif", fontSize: "0.82rem", fontWeight: 400, cursor: "pointer", boxShadow: "0 1px 6px rgba(0,0,0,0.07)", transition: "box-shadow .2s" }}
                onMouseOver={e => e.currentTarget.style.boxShadow = "0 3px 14px rgba(0,0,0,0.13)"}
                onMouseOut={e => e.currentTarget.style.boxShadow = "0 1px 6px rgba(0,0,0,0.07)"}>
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Booking bar — hidden while menu panel is open (panel has its own bar) */}
        {!showMenu && (
          <div style={{ display: "flex", alignItems: "stretch", background: "white", borderRadius: 10, margin: "0 16px 12px", boxShadow: "0 2px 14px rgba(0,0,0,0.09)", overflow: "hidden", height: 58 }}>
            <div style={{ flex: 1.3, padding: "10px 20px", borderRight: "1px solid #EBEBEB", display: "flex", flexDirection: "column", justifyContent: "center" }}>
              <p style={{ fontSize: "0.73rem", fontWeight: 600, marginBottom: 2 }}>Book a stay</p>
              <select value={category} onChange={e => setCategory(e.target.value)} style={sel}>{CATEGORIES.map(c => <option key={c}>{c}</option>)}</select>
            </div>
            <div style={{ flex: 1, padding: "10px 20px", borderRight: "1px solid #EBEBEB", display: "flex", flexDirection: "column", justifyContent: "center" }}>
              <p style={{ fontSize: "0.73rem", fontWeight: 600, marginBottom: 2 }}>Check-In</p>
              <select value={souk} onChange={e => setSouk(e.target.value)} style={sel}>{SOUKS_LIST.map(s => <option key={s}>{s}</option>)}</select>
            </div>
            <div style={{ flex: 1, padding: "10px 20px", borderRight: "1px solid #EBEBEB", display: "flex", flexDirection: "column", justifyContent: "center" }}>
              <p style={{ fontSize: "0.73rem", fontWeight: 600, marginBottom: 2 }}>Check-Out</p>
              <select value={budget} onChange={e => setBudget(e.target.value)} style={sel}>{BUDGETS.map(b => <option key={b}>{b}</option>)}</select>
            </div>
            <button
              style={{ background: "#1C1A17", color: "white", border: "none", padding: "0 26px", fontFamily: "'Jost',sans-serif", fontSize: "0.76rem", letterSpacing: "0.09em", textTransform: "uppercase", cursor: "pointer", whiteSpace: "nowrap", transition: "background .25s" }}
              onMouseOver={e => e.currentTarget.style.background = "#B5451B"}
              onMouseOut={e => e.currentTarget.style.background = "#1C1A17"}>
              Search
            </button>
          </div>
        )}
      </header>

      {/* Menu panel — renders on top of everything */}
      {showMenu && (
        <MenuPanel
          onClose={() => setShowMenu(false)}
          category={category} setCategory={setCategory}
          souk={souk} setSouk={setSouk}
          budget={budget} setBudget={setBudget}
        />
      )}

      {/* Subscribe modal */}
      {showSubscribe && <SubscribeModal onClose={() => setShowSubscribe(false)} />}

      {/* ══════════════════════════════════════════════════════
          HERO
          ══════════════════════════════════════════════════════ */}
      <div style={{ position: "relative", width: "100%", height: "100vh", overflow: "hidden" }}>
        {SLIDE_BG.map((bg, i) => (
          <div key={i} style={{ position: "absolute", inset: 0, background: bg, opacity: i === slide ? 1 : 0, transition: "opacity 1.3s ease" }}>
            <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.17)" }} />
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "14rem", opacity: 0.12, userSelect: "none" }}>{SLIDE_EMOJI[i]}</div>
          </div>
        ))}
        <div style={{ position: "absolute", inset: 0, zIndex: 10, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "0 24px" }}>
          <h1 style={{ ...ha(0.3), fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(1.9rem,3.5vw,3rem)", fontWeight: 300, color: "white", lineHeight: 1.3, maxWidth: 680, textShadow: "0 2px 18px rgba(0,0,0,0.3)", marginBottom: 10 }}>
            {SLIDES[slide].label} — know the fair price before you bargain.
          </h1>
          <p style={{ ...ha(0.5), fontSize: "0.76rem", color: "rgba(255,255,255,0.68)", letterSpacing: "0.13em", textTransform: "uppercase" }}>{SLIDES[slide].sub}</p>
        </div>
        {/* CTAs */}
        <div style={{ position: "absolute", bottom: 78, left: "50%", transform: "translateX(-50%)", zIndex: 10, display: "flex", gap: 16, ...ha(0.7) }}>
          <button onClick={() => navigate('/location')} style={{ display: "flex", alignItems: "center", background: "#B5451B", borderRadius: 50, padding: "12px 24px", border: "none", cursor: "pointer", boxShadow: "0 4px 24px rgba(181,69,27,0.4)", minWidth: 220 }}>
            <div style={{ flex: 1, textAlign: "left" }}>
              <p style={{ fontSize: "0.7rem", color: "rgba(255,255,255,0.8)", marginBottom: 1 }}>Ready to explore?</p>
              <p style={{ fontSize: "0.9rem", fontWeight: 600, color: "white" }}>I Want to Travel</p>
            </div>
            <div style={{ width: 48, height: 48, borderRadius: "50%", background: "rgba(255,255,255,0.2)", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.3rem" }}>✈️</div>
          </button>
          <a href="#prices" style={{ display: "flex", alignItems: "center", background: "white", borderRadius: 50, padding: "7px 7px 7px 26px", textDecoration: "none", boxShadow: "0 4px 24px rgba(0,0,0,0.18)", minWidth: 268 }}>
            <div style={{ flex: 1 }}>
              <p style={{ fontSize: "0.7rem", color: "#888", marginBottom: 1 }}>Find your price</p>
              <p style={{ fontSize: "0.9rem", fontWeight: 600, color: "#1C1A17" }}>Explore our price guide</p>
            </div>
            <div style={{ width: 52, height: 52, borderRadius: "50%", background: SLIDE_BG[slide], flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.5rem", transition: "background 1.3s ease" }}>{SLIDE_EMOJI[slide]}</div>
          </a>
        </div>
        {/* Dots */}
        <div style={{ position: "absolute", bottom: 36, left: "50%", transform: "translateX(-50%)", display: "flex", gap: 6, zIndex: 10 }}>
          {SLIDES.map((_, i) => (
            <button key={i} onClick={() => setSlide(i)} style={{ background: "none", border: "none", cursor: "pointer", padding: "5px 0" }}>
              <div style={{ width: i === slide ? 34 : 22, height: 2.5, borderRadius: 2, background: i === slide ? "white" : "rgba(255,255,255,0.38)", transition: "all .4s ease" }} />
            </button>
          ))}
        </div>
      </div>

      {/* Stats strip */}
      <div style={{ background: "#1C1A17", padding: "20px 80px", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 24 }}>
        {[{ n: "15+", l: "Categories" }, { n: "9", l: "Souks" }, { n: "MAD", l: "Dirham Prices" }, { n: "2025", l: "Edition" }, { n: "CV", l: "AI Detection" }].map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 14 }}>
            {i > 0 && <div style={{ width: 1, height: 30, background: "rgba(255,255,255,0.1)", marginRight: 14 }} />}
            <span style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.8rem", fontWeight: 300, color: "#B5451B" }}>{s.n}</span>
            <span style={{ fontSize: "0.66rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#7a7060" }}>{s.l}</span>
          </div>
        ))}
      </div>

      {/* Price grid */}
      <section id="prices" style={{ background: "#FAF7F2", padding: "90px 80px" }}>
        <Reveal><p style={{ fontSize: "0.64rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#B5451B", marginBottom: 14 }}>2025 / 2026 Price Reference</p></Reveal>
        <Reveal delay={0.1}><h2 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(2.2rem,3.5vw,3.6rem)", fontWeight: 300, lineHeight: 1.1, marginBottom: 56 }}>What you should <em style={{ fontStyle: "italic" }}>actually</em> pay.</h2></Reveal>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 2, border: "1px solid rgba(28,26,23,0.09)" }}>
          {PRICES.map((p, i) => <PriceCard key={i} p={p} delay={i * .08} />)}
        </div>
      </section>

      {/* How it works */}
      <section id="detect" style={{ background: "#1C1A17", padding: "90px 80px" }}>
        <Reveal><p style={{ fontSize: "0.64rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#D4603A", marginBottom: 14 }}>The Technology</p></Reveal>
        <Reveal delay={0.1}><h2 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(2.2rem,3.5vw,3.6rem)", fontWeight: 300, lineHeight: 1.1, color: "white", marginBottom: 56 }}>AI that reads <em style={{ fontStyle: "italic" }}>every price tag.</em></h2></Reveal>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 1, background: "rgba(255,255,255,0.05)" }}>
          {STEPS.map((s, i) => <StepCard key={i} s={s} delay={i * .08} />)}
        </div>
      </section>

      {/* Souk directory */}
      <section id="souks" style={{ background: "#FAF7F2", padding: "90px 80px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 80, alignItems: "center" }}>
        <div>
          <Reveal><p style={{ fontSize: "0.64rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#B5451B", marginBottom: 14 }}>Souk Directory</p></Reveal>
          <Reveal delay={0.1}><h2 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(2.2rem,3.5vw,3.6rem)", fontWeight: 300, lineHeight: 1.1, marginBottom: 18 }}>Find the right <em style={{ fontStyle: "italic" }}>market.</em></h2></Reveal>
          <Reveal delay={0.2}><p style={{ fontSize: "0.93rem", fontWeight: 300, lineHeight: 1.8, color: "#5C5549", marginBottom: 28 }}>Each souk specialises in a different craft. Knowing where to go is half the battle — knowing what to pay is the other half.</p></Reveal>
          <Reveal delay={0.3}>
            <ul style={{ listStyle: "none" }}>
              {SOUKS_DIR.map((s, i) => (
                <li key={i} style={{ display: "flex", alignItems: "center", gap: 14, padding: "12px 0", borderBottom: i < SOUKS_DIR.length - 1 ? "1px solid rgba(28,26,23,0.09)" : "none", fontSize: "0.86rem" }}>
                  <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#B5451B", flexShrink: 0 }} />
                  <span>{s.name}</span>
                  <span style={{ color: "#5C5549", fontSize: "0.74rem", marginLeft: "auto" }}>{s.spec}</span>
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
        <Reveal delay={0.15}>
          <div style={{ background: "linear-gradient(135deg,#c4a882,#8b6542,#5c3e20)", borderRadius: 4, height: 440, position: "relative", overflow: "hidden", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ textAlign: "center", color: "rgba(255,255,255,0.4)" }}>
              <p style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.8rem", fontWeight: 300, marginBottom: 6 }}>Medina Map</p>
              <p style={{ fontSize: "0.68rem", letterSpacing: "0.12em", textTransform: "uppercase" }}>Add your map here</p>
            </div>
            {[{ t: "35%", l: "44%", d: "0s" }, { t: "54%", l: "57%", d: "0.6s" }, { t: "41%", l: "34%", d: "1.1s" }].map((pin, i) => (
              <div key={i} style={{ position: "absolute", top: pin.t, left: pin.l, width: 15, height: 15, background: "#B5451B", borderRadius: "50% 50% 50% 0", transform: "rotate(-45deg)", animation: `pulse 2s ${pin.d} infinite` }} />
            ))}
          </div>
        </Reveal>
      </section>

      <Newsletter />

      <footer style={{ background: "#1C1A17", padding: "60px 80px 30px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: 56, marginBottom: 52 }}>
          <div>
            <p style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.35rem", color: "white", marginBottom: 14 }}>Souk <span style={{ color: "#B5451B" }}>&</span> Price</p>
            <p style={{ fontSize: "0.81rem", color: "#7a7060", lineHeight: 1.7, maxWidth: 260 }}>AI-powered price detection for Marrakech souk products. Know what's fair.</p>
          </div>
          {[
            { t: "Products", l: ["Spices", "Leather", "Textiles", "Ceramics", "Lanterns", "Jewelry"] },
            { t: "Souks", l: ["Souk Semmarine", "Rahba Kedima", "Souk Zrabi", "Souk Haddadine", "Souk Smata"] },
            { t: "Project", l: ["About", "Dataset", "API", "Price Guide", "Contact"] },
          ].map(col => (
            <div key={col.t}>
              <h5 style={{ fontSize: "0.62rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#5c5549", marginBottom: 16 }}>{col.t}</h5>
              <ul style={{ listStyle: "none" }}>{col.l.map(l => <li key={l} style={{ marginBottom: 8 }}><a href="#" style={{ color: "#9d9080", textDecoration: "none", fontSize: "0.82rem" }}>{l}</a></li>)}</ul>
            </div>
          ))}
        </div>
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.07)", paddingTop: 20, display: "flex", justifyContent: "space-between", fontSize: "0.69rem", color: "#5c5549" }}>
          <span>© 2025 Souk & Price</span>
          <span>Price data: Morocco Travel Planner 2025/2026</span>
        </div>
      </footer>

      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        select { -webkit-appearance: none; -moz-appearance: none; appearance: none; }
        @keyframes pulse { 0%,100% { box-shadow: 0 0 0 5px rgba(181,69,27,0.22); } 50% { box-shadow: 0 0 0 11px rgba(181,69,27,0.07); } }
        ::placeholder { color: rgba(255,255,255,0.42) !important; }
      `}</style>
    </div>
  );
}