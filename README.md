
# 🧠👕 Digital Wardrobe AI

Welcome to **Digital Wardrobe AI**, an intelligent multi-agent fashion assistant that helps users:

- Organize their wardrobe digitally.
- Receive outfit recommendations.
- Generate new clothing items based on their style.
- Visualize themselves in 3D wearing these outfits.

The goal is to deliver a functional MVP in 1.5 days using **Streamlit + Pydantic-based AI agents**, allowing each team member to focus on a modular component.

---

## 🧩 Key Features

✅ Upload and manage wardrobe items  
✅ Recommend full outfits based on context (weather, event, preferences)  
✅ Generate new clothes with Generative AI  
✅ Search similar clothes online and link to stores  
✅ 3D try-on preview with user avatar or AI rendering

---

## 🛠️ Technologies & Frameworks

| Tool | Purpose |
|------|---------|
| **Python 3.10+** | Core language |
| **Streamlit** | Web app UI |
| **Pydantic** | Data modeling for each agent |
| **CLIP / BLIP / Hugging Face** | Vision & style embeddings |
| **OpenAI / SD / Replicate** | Generative AI for fashion |
| **FastAPI (optional)** | For backend APIs if needed |
| **CrewAI (not used)** | Considered but not used – custom agent routing instead |

---

## 🚀 Project Setup

```bash
# Clone the repo
git clone https://github.com/your-org/digital-wardrobe-ai.git
cd digital-wardrobe-ai

# Create virtual env
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Make sure to create a `.env` file for storing API keys like:

```env
OPENAI_API_KEY=your_key_here
```

---

## 🧠 Project Structure

```
digital-wardrobe-ai/
├── app.py
├── orchestrator/agent_router.py
├── agents/
│   ├── wardrobe_agent.py
│   ├── recommender_agent.py
│   ├── generator_agent.py
│   ├── tryon_agent.py
├── ui/
│   ├── wardrobe_ui.py
│   ├── recommendation_ui.py
│   ├── generation_ui.py
│   ├── tryon_ui.py
├── services/
├── models/
├── data/
├── assets/
├── utils/
├── requirements.txt
└── README.md
```

---

## 👥 Team Responsibilities

| Member | Component | Files |
|--------|-----------|-------|
| 👤 Member 1 | Wardrobe Upload / Management | `agents/wardrobe_agent.py`, `ui/wardrobe_ui.py` |
| 👤 Member 2 | Outfit Recommender | `agents/recommender_agent.py`, `ui/recommendation_ui.py` |
| 👤 Member 3 | Clothing Generator | `agents/generator_agent.py`, `ui/generation_ui.py` |
| 👤 Member 4 | 3D Try-On Preview | `agents/tryon_agent.py`, `ui/tryon_ui.py` |

All connect via `app.py` and are orchestrated with `agent_router.py`.

---

## 🧪 Sample Flow

1. User uploads clothes (images, metadata)
2. Recommender suggests outfit based on style + weather
3. Generator creates new fashion items based on style profile
4. Visualizer renders user/avatar in chosen outfit
5. Searcher finds similar real-world products online

---

## 💡 Functional Ideas & Enhancements

- **Ψηφιακή ντουλάπα** → Inventory management με metadata (χρώμα, τύπος, ύφασμα, εποχικότητα, mood κλπ).
- **Fashion recommender assistant** → AI που σου λέει τι να φορέσεις με βάση καιρού, περίσταση, προσωπικό στυλ.
- **Generative AI για νέα ρούχα** → δημιουργία outfit ideas / ρούχων βασισμένα στο στυλ του χρήστη.
- **Product search online** → image2product matching (π.χ. reverse image search για παρόμοια ρούχα σε e-shops).
- **Favorites / collections** → διαχείριση αγαπημένων ρούχων, tags, συλλογών.
- **3D visualization** → try-on εμπειρία, avatar του χρήστη σε ρούχα από την ντουλάπα ή γεννήτρια.

---

## 🚀 Τι πρέπει να υλοποιήσουμε:

🔍 **1. AI-Powered Outfit Matching Engine**  
- Συνδύασε τα ρούχα που έχει ο χρήστης για να προτείνεις ολόκληρα outfits, όχι μόνο μεμονωμένα ρούχα.  
- Χρησιμοποίησε embedding μοντέλα (e.g., CLIP) για να αντιστοιχίσεις στυλιστικά items.  
- Πρότεινε "style goals" (e.g. "θέλω να φαίνομαι formal αλλά άνετος σήμερα").

📅 **2. Πρόγραμμα εμφάνισης / wardrobe calendar**  
- Ο χρήστης μπορεί να βλέπει πότε φόρεσε κάτι τελευταία φορά.  
- Προτείνεις ρούχα που δεν έχει φορέσει πρόσφατα, για ανανέωση.

☁️ **3. Καιρός + Περίσταση**  
- Συνδέεις APIs για καιρό, ημερολόγιο/εκδηλώσεις.  
- Π.χ. "Έχει 12°C και meeting στο γραφείο" → προτείνεις casual-formal με layers.

🤖 **4. Ανάλυση προσωπικού στυλ**  
- Ανάλυση των ρούχων του χρήστη (χρώματα, στυλ, brands).  
- Π.χ. "Το στυλ σου είναι Urban Casual με Neutral Colors".

🛒 **5. Σύνδεση με E-commerce APIs**  
- Αν κάνεις generate ρούχα → να τα ματσάρεις με ASOS, Zara, H&M APIs και να βγάζεις links αγοράς.  
- Σκέψου Visual Product Search ή CLIP + e-commerce image search.

🎨 **6. Style customization UI**  
- Ο χρήστης να ορίζει inspiration boards (Pinterest-style) ή icons για να "εκπαιδεύσει" τον assistant.  
- Π.χ. “Θέλω outfits σαν του Timothée Chalamet”.

👗 **7. Virtual try-on με Generative AI ή 3D Avatar**  
- Πιο απλή υλοποίηση: DreamBooth με Stable Diffusion + εικόνες του χρήστη → να τον βάλεις σε generated outfits.  
- Πιο advanced: 3D avatar με pose estimation & try-on (π.χ. Snap AR Lens style).

---

**Let’s build the future of fashion together 💡**
