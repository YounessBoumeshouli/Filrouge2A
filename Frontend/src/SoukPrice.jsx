import { useState, useEffect, useRef } from "react";

/* ── Google Fonts injected once ─────────────────────────────────── */
const FontLink = () => {
  useEffect(() => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href =
      "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Jost:wght@300;400;500;600&display=swap";
    document.head.appendChild(link);
  }, []);
  return null;
};

/* ── DATA ────────────────────────────────────────────────────────── */
const STATS = [
  { num: "15+", label: "Product\nCategories" },
  { num: "9", label: "Souk\nDistricts" },
  { num: "MAD", label: "Real Dirham\nPrices" },
  { num: "2025", label: "Edition\nUpdated" },
  { num: "CV", label: "Computer Vision\nDetection" },
];

const MOSAIC = [
  { emoji: "🌶️", cat: "Spices & Herbs", price: "30–80 MAD / 100g", loc: "Rahba Kedima", grad: "linear-gradient(135deg,#c4a882,#8b6542)", span: "col-span-5 row-span-1" },
  { emoji: "👟", cat: "Leather Goods", price: "80–600 MAD", loc: "Souk Smata", grad: "linear-gradient(135deg,#b5451b,#7a2d10)", span: "col-span-3 row-span-2" },
  { emoji: "🏮", cat: "Brass Lanterns", price: "100–800 MAD", loc: "Souk Haddadine", grad: "linear-gradient(135deg,#8c7355,#5c4a30)", span: "col-span-4 row-span-1" },
  { emoji: "🍶", cat: "Argan Oil", price: "150–300 MAD", loc: "Souk El Attarine", grad: "linear-gradient(135deg,#d4b896,#a07850)", span: "col-span-3 row-span-1" },
  { emoji: "🪬", cat: "Jewelry", price: "100–3000 MAD", loc: "Souk des Bijoutiers", grad: "linear-gradient(135deg,#6b8c6b,#3d5c3d)", span: "col-span-2 row-span-1" },
  { emoji: "🧺", cat: "Textiles & Rugs", price: "300–5000+ MAD", loc: "Souk Zrabi", grad: "linear-gradient(135deg,#c8a870,#8c6830)", span: "col-span-4 row-span-1" },
];

const PRICES = [
  { cat: "Leather", name: "Babouches (Slippers)", arabic: "بلغة", souk: "Souk Smata / Souk Cherratine", range: "80–150", unit: "MAD per pair", note: "Traditional pointed-toe leather. Price rises with embroidery quality." },
  { cat: "Spices", name: "Spices & Herbs", arabic: "بهارات", souk: "Rahba Kedima / Souk Ableuh", range: "30–80", unit: "MAD per 100g", note: "Cumin, saffron, ras el hanout. Weighed fresh at stall." },
  { cat: "Argan", name: "Argan Oil", arabic: "زيت أركان", souk: "Souk El Attarine / Arganino", range: "150–300", unit: "MAD per bottle", note: "Real oil = thick paste + strong nut aroma. Avoid watery versions." },
  { cat: "Crafts", name: "Tagine Pot", arabic: "طاجين", souk: "Souk Semmarine", range: "20–50", unit: "MAD each", note: "Decorative or functional clay cooking pots, hand-painted." },
  { cat: "Lanterns", name: "Moroccan Lantern", arabic: "فانوس مغربي", souk: "Souk Haddadine", range: "100–800", unit: "MAD, by size", note: "Metal and coloured glass. Creates stunning shadow patterns when lit." },
  { cat: "Textiles", name: "Berber Carpet", arabic: "زربية بربرية", souk: "Souk Zrabi", range: "800–5,000+", unit: "MAD handwoven", note: "Beni Ourain rugs prized for craftsmanship. Shipping usually available." },
];

const STEPS = [
  { num: "01", icon: "📷", title: "Capture", desc: "Photograph any price tag or product in the Marrakech souk with your phone camera." },
  { num: "02", icon: "🔍", title: "Detect", desc: "Computer vision locates and isolates the price region, even on busy market stalls." },
  { num: "03", icon: "🧠", title: "Extract", desc: "OCR reads prices in MAD — from handwritten tags, Arabic numerals, and partial labels." },
  { num: "04", icon: "✅", title: "Compare", desc: "Detected price is instantly checked against our 2025/2026 fair price database." },
];

const SOUKS = [
  { name: "Souk Semmarine", specialty: "Bags, shoes, pottery, fabrics" },
  { name: "Souk Smata", specialty: "Babouches & leather slippers" },
  { name: "Souk Zrabi", specialty: "Handmade carpets & rugs" },
  { name: "Souk Cherratine", specialty: "Leather bags, belts, wallets" },
  { name: "Rahba Kedima", specialty: "Spices, herbs, rosewater" },
  { name: "Souk Haddadine", specialty: "Blacksmiths & brass lanterns" },
  { name: "Souk des Bijoutiers", specialty: "Silver & Berber jewelry" },
  { name: "Souk Chouari", specialty: "Wood, baskets, games" },
  { name: "Souk El Attarine", specialty: "Argan oil & perfumes" },
];

/* ── HOOKS ───────────────────────────────────────────────────────── */
function useScrollReveal() {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVisible(true); },
      { threshold: 0.12 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  return [ref, visible];
}

function useCursor() {
  const [pos, setPos] = useState({ x: -100, y: -100 });
  const [hovering, setHovering] = useState(false);
  useEffect(() => {
    const move = (e) => setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", move);
    return () => window.removeEventListener("mousemove", move);
  }, []);
  return { pos, hovering, setHovering };
}

/* ── SUB-COMPONENTS ──────────────────────────────────────────────── */
function Reveal({ children, delay = 0, className = "" }) {
  const [ref, visible] = useScrollReveal();
  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(28px)",
        transition: `opacity 0.7s ease ${delay}s, transform 0.7s ease ${delay}s`,
      }}
    >
      {children}
    </div>
  );
}

function MosaicItem({ item, onHover }) {
  const [hovered, setHovered] = useState(false);
  const gridStyles = {
    0: { gridColumn: "1 / 6", gridRow: "1 / 2" },
    1: { gridColumn: "6 / 9", gridRow: "1 / 3" },
    2: { gridColumn: "9 / 13", gridRow: "1 / 2" },
    3: { gridColumn: "1 / 4", gridRow: "2 / 3" },
    4: { gridColumn: "4 / 6", gridRow: "2 / 3" },
    5: { gridColumn: "9 / 13", gridRow: "2 / 3" },
  };
  const idx = MOSAIC.indexOf(item);
  return (
    <div
      style={{
        ...gridStyles[idx],
        position: "relative",
        overflow: "hidden",
        cursor: "none",
        background: item.grad,
      }}
      onMouseEnter={() => { setHovered(true); onHover(true); }}
      onMouseLeave={() => { setHovered(false); onHover(false); }}
    >
      <div style={{
        width: "100%", height: "100%",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: "3.5rem",
        transform: hovered ? "scale(1.08)" : "scale(1)",
        transition: "transform 0.7s cubic-bezier(0.25,0.46,0.45,0.94)",
        filter: hovered ? "saturate(1.2)" : "saturate(0.85)",
      }}>
        {item.emoji}
      </div>
      <div style={{
        position: "absolute", inset: 0,
        background: "linear-gradient(to top, rgba(28,26,23,0.75) 0%, transparent 55%)",
        opacity: hovered ? 1 : 0,
        transition: "opacity 0.4s",
        display: "flex", alignItems: "flex-end",
        padding: "24px",
      }}>
        <div>
          <h4 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.4rem", fontWeight: 400, color: "white" }}>{item.cat}</h4>
          <p style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.75)", marginTop: 4, letterSpacing: "0.04em" }}>{item.price} · {item.loc}</p>
        </div>
      </div>
    </div>
  );
}

function PriceCard({ p, delay, onHover }) {
  const [hovered, setHovered] = useState(false);
  const catColors = {
    Leather: "#8B4513", Spices: "#e67e22", Argan: "#16a085",
    Crafts: "#27ae60", Lanterns: "#f39c12", Textiles: "#8e44ad",
  };
  return (
    <div
      onMouseEnter={() => { setHovered(true); onHover(true); }}
      onMouseLeave={() => { setHovered(false); onHover(false); }}
      style={{
        background: hovered ? "#fff" : "#FAF7F2",
        padding: "36px 32px",
        borderRight: "1px solid rgba(28,26,23,0.1)",
        transition: "background 0.3s",
        cursor: "none",
      }}
    >
      <p style={{ fontSize: "0.65rem", letterSpacing: "0.15em", textTransform: "uppercase", color: catColors[p.cat] || "#B5451B", marginBottom: 10 }}>{p.cat}</p>
      <h3 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.5rem", fontWeight: 400, marginBottom: 6, lineHeight: 1.2 }}>{p.name}</h3>
      <span style={{ direction: "rtl", display: "block", color: "#5C5549", fontSize: "0.85rem", fontFamily: "'Cormorant Garamond',serif", fontStyle: "italic", marginBottom: 16 }}>{p.arabic}</span>
      <p style={{ fontSize: "0.75rem", color: "#5C5549", marginBottom: 20, display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ display: "inline-block", width: 14, height: 1, background: "#B5451B" }} />
        {p.souk}
      </p>
      <span style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "2.2rem", fontWeight: 300, color: "#1C1A17" }}>{p.range}</span>
      <p style={{ fontSize: "0.72rem", color: "#5C5549", marginTop: 2 }}>{p.unit}</p>
      <p style={{ marginTop: 18, paddingTop: 18, borderTop: "1px solid rgba(28,26,23,0.1)", fontSize: "0.78rem", color: "#5C5549", lineHeight: 1.65 }}>{p.note}</p>
    </div>
  );
}

/* ── MAIN COMPONENT ──────────────────────────────────────────────── */
export default function SoukPrice() {
  const { pos, hovering, setHovering } = useCursor();
  const [scrolled, setScrolled] = useState(false);
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);
  const [heroVisible, setHeroVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setHeroVisible(true), 100);
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener("scroll", onScroll);
    return () => { clearTimeout(t); window.removeEventListener("scroll", onScroll); };
  }, []);

  const hoverOn = () => setHovering(true);
  const hoverOff = () => setHovering(false);

  const anim = (delay = 0) => ({
    opacity: heroVisible ? 1 : 0,
    transform: heroVisible ? "translateY(0)" : "translateY(24px)",
    transition: `opacity 0.8s ease ${delay}s, transform 0.8s ease ${delay}s`,
  });

  return (
    <div style={{ fontFamily: "'Jost',sans-serif", background: "#F5F0E8", color: "#1C1A17", overflowX: "hidden", cursor: "none" }}>
      <FontLink />

      {/* ── CUSTOM CURSOR ── */}
      <div style={{
        position: "fixed", top: pos.y, left: pos.x,
        width: hovering ? 40 : 10, height: hovering ? 40 : 10,
        background: hovering ? "rgba(181,69,27,0.3)" : "#B5451B",
        borderRadius: "50%",
        transform: "translate(-50%,-50%)",
        pointerEvents: "none", zIndex: 9999,
        transition: "width 0.3s, height 0.3s, background 0.3s",
        mixBlendMode: "multiply",
      }} />

      {/* ── HEADER ── */}
      <header style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: scrolled ? "14px 48px" : "22px 48px",
        background: "rgba(245,240,232,0.92)",
        backdropFilter: "blur(12px)",
        borderBottom: "1px solid rgba(28,26,23,0.12)",
        transition: "padding 0.4s ease",
      }}>
        <a href="#" style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.5rem", fontWeight: 400, textDecoration: "none", color: "#1C1A17", letterSpacing: "0.02em" }}
          onMouseEnter={hoverOn} onMouseLeave={hoverOff}>
          Souk <span style={{ color: "#B5451B" }}>&</span> Price
        </a>
        <nav style={{ display: "flex", gap: 32, alignItems: "center" }}>
          {["Products", "Prices", "Souks", "About"].map(item => (
            <a key={item} href={`#${item.toLowerCase()}`}
              onMouseEnter={hoverOn} onMouseLeave={hoverOff}
              style={{ fontFamily: "'Jost',sans-serif", fontSize: "0.72rem", letterSpacing: "0.12em", textTransform: "uppercase", color: "#5C5549", textDecoration: "none", transition: "color 0.25s" }}
              onMouseOver={e => e.target.style.color = "#1C1A17"}
              onMouseOut={e => e.target.style.color = "#5C5549"}>
              {item}
            </a>
          ))}
          <a href="#detect" onMouseEnter={hoverOn} onMouseLeave={hoverOff}
            style={{ background: "#B5451B", color: "white", fontFamily: "'Jost',sans-serif", fontSize: "0.72rem", letterSpacing: "0.1em", textTransform: "uppercase", padding: "10px 22px", borderRadius: 2, textDecoration: "none", transition: "background 0.25s" }}
            onMouseOver={e => e.target.style.background = "#D4603A"}
            onMouseOut={e => e.target.style.background = "#B5451B"}>
            Detect a Price
          </a>
        </nav>
      </header>

      {/* ── HERO ── */}
      <section id="home" style={{ minHeight: "100vh", paddingTop: 90, display: "grid", gridTemplateColumns: "1fr 1fr" }}>
        {/* Left */}
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", padding: "80px 60px 80px 80px", position: "relative" }}>
          <p style={{ ...anim(0.2), fontFamily: "'Jost',sans-serif", fontSize: "0.68rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#B5451B", marginBottom: 24 }}>
            Marrakech · 2025 / 2026 Edition
          </p>
          <h1 style={{ ...anim(0.4), fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(3.5rem, 5.5vw, 6rem)", fontWeight: 300, lineHeight: 1.06, letterSpacing: "-0.01em", marginBottom: 28 }}>
            Know the<br />
            <em style={{ fontStyle: "italic", color: "#B5451B" }}>fair price</em><br />
            before you<br />
            bargain.
          </h1>
          <p style={{ ...anim(0.6), fontSize: "1rem", fontWeight: 300, lineHeight: 1.8, color: "#5C5549", maxWidth: 380, marginBottom: 48 }}>
            An intelligent price guide for Marrakech's iconic souks. From hand-stitched babouches to rare Berber rugs — shop confidently with real market data.
          </p>
          <div style={{ ...anim(0.8), display: "flex", gap: 20, alignItems: "center" }}>
            <a href="#detect" onMouseEnter={hoverOn} onMouseLeave={hoverOff}
              style={{ background: "#1C1A17", color: "white", fontFamily: "'Jost',sans-serif", fontSize: "0.72rem", letterSpacing: "0.1em", textTransform: "uppercase", padding: "16px 32px", borderRadius: 2, textDecoration: "none", transition: "background 0.25s" }}
              onMouseOver={e => e.target.style.background = "#B5451B"}
              onMouseOut={e => e.target.style.background = "#1C1A17"}>
              Detect a Price
            </a>
            <a href="#prices" onMouseEnter={hoverOn} onMouseLeave={hoverOff}
              style={{ fontFamily: "'Jost',sans-serif", fontSize: "0.72rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#5C5549", textDecoration: "none", display: "flex", alignItems: "center", gap: 10, transition: "color 0.25s" }}
              onMouseOver={e => e.target.style.color = "#1C1A17"}
              onMouseOut={e => e.target.style.color = "#5C5549"}>
              Browse Prices →
            </a>
          </div>
          {/* Scroll indicator */}
          <div style={{ ...anim(1.2), position: "absolute", bottom: 40, left: 80, display: "flex", alignItems: "center", gap: 12, fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#5C5549" }}>
            <div style={{ width: 40, height: 1, background: "#5C5549", position: "relative", overflow: "hidden" }}>
              <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, background: "#B5451B", animation: "slideRight 2s 1.5s infinite" }} />
            </div>
            Scroll to explore
          </div>
        </div>

        {/* Right image panel */}
        <div style={{ ...anim(0.3), position: "relative", overflow: "hidden" }}>
          <div style={{ width: "100%", height: "100%", background: "linear-gradient(160deg,#c4a882 0%,#8b6542 40%,#5c3e20 100%)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ textAlign: "center", color: "rgba(255,255,255,0.35)" }}>
              <div style={{ fontSize: "6rem", lineHeight: 1 }}>🏺</div>
              <div style={{ fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase", marginTop: 12 }}>Replace with hero image</div>
            </div>
          </div>
          {/* Floating badge */}
          <div style={{ position: "absolute", bottom: 48, left: -24, background: "#F5F0E8", border: "1px solid rgba(28,26,23,0.12)", padding: "20px 28px", display: "flex", alignItems: "center", gap: 16, boxShadow: "0 8px 32px rgba(0,0,0,0.08)" }}>
            <div style={{ width: 40, height: 40, background: "#B5451B", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontSize: "1.1rem" }}>📷</div>
            <div style={{ fontSize: "0.8rem" }}>
              <strong style={{ display: "block", fontWeight: 500, fontSize: "0.95rem" }}>AI Price Detection</strong>
              <span style={{ color: "#5C5549", fontSize: "0.72rem" }}>Powered by Computer Vision</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── STATS STRIP ── */}
      <div style={{ background: "#1C1A17", color: "white", padding: "20px 80px", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 48, overflow: "hidden" }}>
        {STATS.map((s, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 16 }}>
            {i > 0 && <div style={{ width: 1, height: 40, background: "rgba(255,255,255,0.12)", marginRight: 16 }} />}
            <span style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "2rem", fontWeight: 300, color: "#B5451B" }}>{s.num}</span>
            <span style={{ fontSize: "0.7rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#a09880", lineHeight: 1.5, whiteSpace: "pre-line" }}>{s.label}</span>
          </div>
        ))}
      </div>

      {/* ── MOSAIC ── */}
      <div id="products" style={{ background: "#FAF7F2", paddingBottom: 100 }}>
        <div style={{ padding: "80px 80px 48px 80px", display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
          <div style={{ maxWidth: 520 }}>
            <Reveal><p style={{ fontSize: "0.68rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#B5451B", marginBottom: 16 }}>What We Cover</p></Reveal>
            <Reveal delay={0.1}><h2 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(2.4rem, 3.5vw, 3.8rem)", fontWeight: 300, lineHeight: 1.1, marginBottom: 20 }}>Every corner of<br /><em style={{ fontStyle: "italic" }}>the medina</em>, priced.</h2></Reveal>
            <Reveal delay={0.2}><p style={{ fontSize: "0.95rem", fontWeight: 300, lineHeight: 1.8, color: "#5C5549" }}>From fragrant spice stalls of Rahba Kedima to the gleaming lanterns of Souk Haddadine — we track fair prices across every district.</p></Reveal>
          </div>
          <Reveal delay={0.2}>
            <a href="#prices" onMouseEnter={hoverOn} onMouseLeave={hoverOff}
              style={{ fontFamily: "'Jost',sans-serif", fontSize: "0.72rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#5C5549", textDecoration: "none", display: "flex", alignItems: "center", gap: 10, whiteSpace: "nowrap" }}>
              View all prices →
            </a>
          </Reveal>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(12,1fr)", gridTemplateRows: "300px 300px", gap: 3, padding: "0 3px" }}>
          {MOSAIC.map((item, i) => (
            <MosaicItem key={i} item={item} onHover={i % 2 === 0 ? hoverOn : hoverOff} />
          ))}
        </div>
      </div>

      {/* ── PRICE TABLE ── */}
      <section id="prices" style={{ background: "#F5F0E8", padding: "100px 80px" }}>
        <Reveal><p style={{ fontSize: "0.68rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#B5451B", marginBottom: 16 }}>2025 / 2026 Price Reference</p></Reveal>
        <Reveal delay={0.1}><h2 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(2.4rem,3.5vw,3.8rem)", fontWeight: 300, lineHeight: 1.1, marginBottom: 60 }}>What you should<br /><em style={{ fontStyle: "italic" }}>actually</em> pay.</h2></Reveal>

        {[PRICES.slice(0, 3), PRICES.slice(3)].map((row, ri) => (
          <div key={ri} style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 2, marginBottom: 2, border: "1px solid rgba(28,26,23,0.1)", borderBottom: ri === 0 ? "none" : undefined }}>
            {row.map((p, pi) => (
              <Reveal key={pi} delay={pi * 0.1}>
                <PriceCard p={p} delay={pi * 0.1} onHover={pi % 2 === 0 ? hoverOn : hoverOff} />
              </Reveal>
            ))}
          </div>
        ))}
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="detect" style={{ background: "#1C1A17", color: "white", padding: "100px 80px" }}>
        <Reveal><p style={{ fontSize: "0.68rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#D4603A", marginBottom: 16 }}>The Technology</p></Reveal>
        <Reveal delay={0.1}><h2 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(2.4rem,3.5vw,3.8rem)", fontWeight: 300, lineHeight: 1.1, color: "white", marginBottom: 60 }}>AI that reads<br /><em style={{ fontStyle: "italic" }}>every price tag.</em></h2></Reveal>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 1, background: "rgba(255,255,255,0.06)" }}>
          {STEPS.map((s, i) => (
            <Reveal key={i} delay={i * 0.1}>
              <StepCard s={s} onHover={hoverOn} onLeave={hoverOff} />
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── SOUK MAP ── */}
      <div id="souks" style={{ background: "#FAF7F2", padding: 80, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 80, alignItems: "center" }}>
        <div>
          <Reveal><p style={{ fontSize: "0.68rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#B5451B", marginBottom: 16 }}>Souk Directory</p></Reveal>
          <Reveal delay={0.1}><h2 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(2.4rem,3.5vw,3.8rem)", fontWeight: 300, lineHeight: 1.1, marginBottom: 20 }}>Find the right<br /><em style={{ fontStyle: "italic" }}>market.</em></h2></Reveal>
          <Reveal delay={0.2}><p style={{ fontSize: "0.95rem", fontWeight: 300, lineHeight: 1.8, color: "#5C5549", marginBottom: 32 }}>Each souk specialises in a different craft. Knowing where to go is half the battle — knowing what to pay is the other half.</p></Reveal>
          <Reveal delay={0.3}>
            <ul style={{ listStyle: "none" }}>
              {SOUKS.map((souk, i) => (
                <li key={i} style={{ display: "flex", alignItems: "center", gap: 16, padding: "13px 0", borderBottom: i < SOUKS.length - 1 ? "1px solid rgba(28,26,23,0.1)" : "none", fontSize: "0.87rem" }}
                  onMouseEnter={hoverOn} onMouseLeave={hoverOff}>
                  <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#B5451B", flexShrink: 0 }} />
                  <span style={{ fontWeight: 400 }}>{souk.name}</span>
                  <span style={{ color: "#5C5549", fontSize: "0.75rem", marginLeft: "auto" }}>{souk.specialty}</span>
                </li>
              ))}
            </ul>
          </Reveal>
        </div>

        <Reveal delay={0.2}>
          <div style={{ background: "linear-gradient(135deg,#c4a882 0%,#8b6542 50%,#5c3e20 100%)", borderRadius: 4, height: 460, position: "relative", overflow: "hidden", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ textAlign: "center", color: "rgba(255,255,255,0.5)" }}>
              <h3 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "2rem", fontWeight: 300, marginBottom: 8 }}>Medina Map</h3>
              <p style={{ fontSize: "0.72rem", letterSpacing: "0.1em", textTransform: "uppercase" }}>Add your map here</p>
            </div>
            {[{ top: "35%", left: "45%", delay: "0s" }, { top: "55%", left: "58%", delay: "0.5s" }, { top: "42%", left: "35%", delay: "1s" }].map((pin, i) => (
              <div key={i} style={{ position: "absolute", top: pin.top, left: pin.left, width: 16, height: 16, background: "#B5451B", borderRadius: "50% 50% 50% 0", transform: "rotate(-45deg)", animation: `pulse 2s ${pin.delay} infinite` }} />
            ))}
          </div>
        </Reveal>
      </div>

      {/* ── NEWSLETTER ── */}
      <div style={{ background: "#B5451B", padding: "100px 80px", textAlign: "center" }}>
        <Reveal>
          <h2 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "clamp(2.5rem,4vw,4rem)", fontWeight: 300, color: "white", lineHeight: 1.1, marginBottom: 16 }}>
            Shop Marrakech with<br /><em style={{ fontStyle: "italic" }}>confidence.</em>
          </h2>
        </Reveal>
        <Reveal delay={0.1}><p style={{ color: "rgba(255,255,255,0.75)", fontSize: "0.95rem", fontWeight: 300, marginBottom: 48 }}>Get price alerts and new souk guides delivered to your inbox.</p></Reveal>
        <Reveal delay={0.2}>
          {subscribed ? (
            <p style={{ color: "white", fontFamily: "'Cormorant Garamond',serif", fontSize: "1.4rem", fontStyle: "italic" }}>✓ You're in! We'll be in touch.</p>
          ) : (
            <div style={{ display: "flex", maxWidth: 480, margin: "0 auto" }}>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="Your email address"
                onMouseEnter={hoverOn} onMouseLeave={hoverOff}
                style={{ flex: 1, background: "rgba(255,255,255,0.15)", border: "1px solid rgba(255,255,255,0.3)", borderRight: "none", padding: "16px 22px", color: "white", fontFamily: "'Jost',sans-serif", fontSize: "0.9rem", outline: "none", borderRadius: "2px 0 0 2px" }}
              />
              <button
                onClick={() => email && setSubscribed(true)}
                onMouseEnter={hoverOn} onMouseLeave={hoverOff}
                style={{ background: "white", color: "#B5451B", border: "none", padding: "16px 28px", fontFamily: "'Jost',sans-serif", fontSize: "0.72rem", letterSpacing: "0.1em", textTransform: "uppercase", cursor: "none", fontWeight: 500, borderRadius: "0 2px 2px 0", transition: "background 0.25s" }}
                onMouseOver={e => { e.target.style.background = "#1C1A17"; e.target.style.color = "white"; }}
                onMouseOut={e => { e.target.style.background = "white"; e.target.style.color = "#B5451B"; }}>
                Subscribe
              </button>
            </div>
          )}
        </Reveal>
      </div>

      {/* ── FOOTER ── */}
      <footer style={{ background: "#1C1A17", color: "white", padding: "64px 80px 36px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: 60, marginBottom: 60 }}>
          <div>
            <span style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.4rem", color: "white", display: "block", marginBottom: 16 }}>
              Souk <span style={{ color: "#B5451B" }}>&</span> Price
            </span>
            <p style={{ fontSize: "0.82rem", color: "#7a7060", lineHeight: 1.7, maxWidth: 280 }}>An AI-powered price detection tool for Marrakech souk products. Know what's fair. Shop with confidence.</p>
          </div>
          {[
            { title: "Products", links: ["Spices", "Leather", "Textiles", "Ceramics", "Lanterns", "Jewelry"] },
            { title: "Souks", links: ["Souk Semmarine", "Rahba Kedima", "Souk Zrabi", "Souk Haddadine", "Souk Smata"] },
            { title: "Project", links: ["About", "Dataset", "API", "Price Guide", "Contact"] },
          ].map(col => (
            <div key={col.title}>
              <h5 style={{ fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#5c5549", marginBottom: 20 }}>{col.title}</h5>
              <ul style={{ listStyle: "none" }}>
                {col.links.map(l => (
                  <li key={l} style={{ marginBottom: 10 }}>
                    <a href="#" onMouseEnter={hoverOn} onMouseLeave={hoverOff}
                      style={{ color: "#9d9080", textDecoration: "none", fontSize: "0.85rem", transition: "color 0.25s" }}
                      onMouseOver={e => e.target.style.color = "white"}
                      onMouseOut={e => e.target.style.color = "#9d9080"}>
                      {l}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div style={{ borderTop: "1px solid rgba(255,255,255,0.08)", paddingTop: 24, display: "flex", justifyContent: "space-between", fontSize: "0.72rem", color: "#5c5549", letterSpacing: "0.05em" }}>
          <span>© 2025 Souk & Price — Marrakech Price Detection Project</span>
          <span>Price data: Morocco Travel Planner 2025/2026</span>
        </div>
      </footer>

      {/* ── KEYFRAMES ── */}
      <style>{`
        @keyframes slideRight { 0% { left: -100%; } 100% { left: 100%; } }
        @keyframes pulse { 0%,100% { box-shadow: 0 0 0 5px rgba(181,69,27,0.25); } 50% { box-shadow: 0 0 0 10px rgba(181,69,27,0.08); } }
        * { cursor: none !important; }
        ::placeholder { color: rgba(255,255,255,0.45) !important; }
      `}</style>
    </div>
  );
}

/* ── STEP CARD (extracted to avoid hooks-in-loop) ─────────────────── */
function StepCard({ s, onHover, onLeave }) {
  const [hovered, setHovered] = useState(false);
  return (
    <div
      onMouseEnter={() => { setHovered(true); onHover(); }}
      onMouseLeave={() => { setHovered(false); onLeave(); }}
      style={{ background: hovered ? "#2a2722" : "#1C1A17", padding: "48px 36px", borderRight: "1px solid rgba(255,255,255,0.07)", transition: "background 0.3s", cursor: "none" }}>
      <div style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "3.5rem", fontWeight: 300, color: "rgba(181,69,27,0.25)", lineHeight: 1, marginBottom: 28 }}>{s.num}</div>
      <div style={{ width: 48, height: 48, background: "rgba(181,69,27,0.15)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 24, fontSize: "1.3rem" }}>{s.icon}</div>
      <h4 style={{ fontFamily: "'Cormorant Garamond',serif", fontSize: "1.4rem", fontWeight: 400, marginBottom: 12, color: "white" }}>{s.title}</h4>
      <p style={{ fontSize: "0.85rem", lineHeight: 1.75, color: "#9d9080", fontWeight: 300 }}>{s.desc}</p>
    </div>
  );
}
