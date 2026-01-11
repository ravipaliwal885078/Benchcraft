# 🪟 Windows Setup Guide - BenchCraft AI

## ⚠️ Important: C++ Build Tools Required

ChromaDB requires Microsoft Visual C++ 14.0 or greater to build on Windows. You have two options:

### Option 1: Install C++ Build Tools (Recommended for Full Functionality)

1. Download and install **Microsoft C++ Build Tools**:
   - Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   -or
   -winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--passive --wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
   - Download and run the installer
   - Select "C++ build tools" workload
   - Install (this is a large download ~6GB)

2. After installation, restart your terminal and run:
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

### Option 2: Use Pre-built ChromaDB (Workaround)

If you want to proceed without building tools, we can modify the setup. However, this may have limitations.

---

## 🚀 Quick Setup Steps

### Step 1: Create `.env` File

```powershell
cd backend
@"
GEMINI_API_KEY=your_actual_gemini_api_key_here
"@ | Out-File -FilePath .env -Encoding utf8
```

**⚠️ IMPORTANT**: Replace `your_actual_gemini_api_key_here` with your real Gemini API key from https://makersuite.google.com/app/apikey

### Step 2: Install Dependencies

After installing C++ Build Tools (Option 1 above):

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you encounter the chroma-hnswlib error, you need the C++ Build Tools (see Option 1).

### Step 3: Seed Database

```powershell
python seed.py
```

This creates:
- SQLite database at `data/benchcraft.db`
- ChromaDB vector store at `data/chroma_store`
- 20 sample employees
- 5 sample projects

### Step 4: Start Backend

```powershell
python app.py
```

Backend will run on: **http://localhost:5000**

### Step 5: Install Frontend Dependencies (New Terminal)

```powershell
cd frontend
npm install
npm run dev
```

Frontend will run on: **http://localhost:3000**

---

## 🐛 Troubleshooting

### "Microsoft Visual C++ 14.0 or greater is required"

**Solution**: Install Microsoft C++ Build Tools (see Option 1 above)

### "GEMINI_API_KEY not found" or "Authentication Error"

**Solution**: Make sure you created `backend\.env` file with your Gemini API key

### "Port already in use"

**Solution**: Kill the process using the port or change ports in config files

---

## ✅ Success Checklist

- [ ] C++ Build Tools installed (for ChromaDB)
- [ ] `.env` file created with Gemini API key
- [ ] Backend dependencies installed
- [ ] Database seeded (`python seed.py`)
- [ ] Backend running on port 5000
- [ ] Frontend dependencies installed
- [ ] Frontend running on port 3000
- [ ] Can access app at http://localhost:3000

---

## 🎯 Next Steps After Setup

1. Open http://localhost:3000 in your browser
2. Explore the Dashboard
3. Try searching for talent in the Marketplace
4. Create projects in the Pipeline page
5. View allocations in the Canvas page

---

**Note**: The C++ Build Tools installation is a one-time setup that enables ChromaDB (vector database) functionality. This is required for the semantic search features.
