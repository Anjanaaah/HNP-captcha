from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

model_id = "C:/mini_project1"

print("Loading model...")

model = Qwen2VLForConditionalGeneration.from_pretrained(
    model_id,
    device_map="cpu",
    local_files_only=True
)

processor = AutoProcessor.from_pretrained(
    model_id,
    local_files_only=True
)

print("Model loaded successfully!")
