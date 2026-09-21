import gradio as gr
from main import app

# Status dashboard shown at root URL
with gr.Blocks(title="AI Travel Planner API") as demo:
    gr.Markdown("# ✈️ AI Travel Planner API is Live")
    gr.Markdown("FastAPI backend is active with endpoints `/health`, `/api/chat`, and `/api/chat/stream`.")

# Mount your existing FastAPI app directly onto Gradio
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
