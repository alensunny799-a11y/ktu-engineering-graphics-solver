from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router  # This points directly to your updated routes file

app = FastAPI(title="KTU Engineering Graphics AI Solver")

# ALLOW ALL ORIGINS - This tells the browser that your local HTML file 
# is safely allowed to pull data from your FastAPI server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your File:// protocol to connect instantly!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our drawing engine pathways
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)    