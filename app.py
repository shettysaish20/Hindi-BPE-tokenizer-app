import gradio as gr
import hindi_tokenizer
import json
import random

pattern = r"(?i:[sdmt]|ll|ve|re)|\s?[\u0900-\u0963\u097A-\u097F]+|[\u0966-\u096F]{1,3}|[\d]{1,3}|\s?[a-zA-Z]+|[।.,!?;:\"'(){}[\]-\u0964\u0965]|[^\s\w\u0900-\u097F]|\s*[\r\n]|\s+(?!\S)|\s+"

# Load the model
model = hindi_tokenizer.RegexTokenizer(pattern=pattern)
model.load("hindi_tokenizer.model")

sample_texts = [
    "नमस्ते दुनिया! यह एक हिंदी वाक्य है जिसका उपयोग परीक्षण के लिए किया जा रहा है। यह देखने के लिए कि क्या टोकननाइज़र ठीक से काम करता है, हम विभिन्न प्रकार के वाक्यों और शब्दों का उपयोग करेंगे।",
    "भारत एक महान देश है। यहाँ विभिन्न संस्कृतियाँ और भाषाएँ हैं। लोग मिलनसार और सहायक हैं।",
    "मेरा नाम GitHub Copilot है। मैं एक AI सहायक हूँ और मैं आपके सवालों के जवाब देने और कार्यों को पूरा करने में मदद कर सकता हूँ।",
    "आज मौसम बहुत अच्छा है। सूरज चमक रहा है और हवा में ठंडक है। यह दिन बाहर घूमने और प्रकृति का आनंद लेने के लिए बिल्कुल सही है।",
    "कंप्यूटर विज्ञान एक रोमांचक क्षेत्र है जो तेजी से विकसित हो रहा है। नई तकनीकें हर समय विकसित हो रही हैं, और कंप्यूटर वैज्ञानिकों को इन परिवर्तनों के साथ बने रहने की आवश्यकता है।"
]

def tokenize_and_compare(text):
    """
    Tokenizes the input text using the loaded model, calculates the number of tokens,
    and computes the compression ratio compared to UTF-8 encoding.
    Also returns a highlighted version of the tokenized text.
    """
    tokens = model.encode(text)
    num_tokens = len(tokens)

    utf8_length = len(text.encode('utf-8'))
    compression_ratio = utf8_length / num_tokens if num_tokens > 0 else 0

    # Highlighted text with token IDs
    highlighted_text = ""
    token_json = {}
    # start = 0
    for token_id in tokens:
        token = model.decode([token_id])
        # end = start + len(token)
        color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Generate random color
        highlighted_text += f"<span style='background-color:{color};'>{token}</span>"
        if token not in token_json.keys():
            token_json[token] = token_id
        # start = end

    return tokens, num_tokens, compression_ratio, highlighted_text, token_json


def decode_text(token_ids_str):
    """
    Decodes a list of token IDs back into text.
    """
    try:
        token_ids = json.loads(token_ids_str)
        if not isinstance(token_ids, list):
            return "Error: Input must be a list of integers."
        for token_id in token_ids:
            if not isinstance(token_id, int):
                return "Error: Input must be a list of integers."
        decoded_text = model.decode(token_ids)
        return decoded_text
    except json.JSONDecodeError:
        return "Error: Invalid JSON format."
    except Exception as e:
        return f"Error: {str(e)}"


def gradio_interface(text):
    """
    Gradio interface function to process text and return results.
    """
    tokens, num_tokens, compression_ratio, highlighted_text, token_json = tokenize_and_compare(text)

    return tokens, highlighted_text, num_tokens, f"{compression_ratio:.2f}", json.dumps(token_json, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    with gr.Blocks() as iface:
        gr.Markdown(
            """# Hindi BPE Tokenizer
            This app tokenizes Hindi text using a custom Regex-based splitting BPE tokenizer.
            """
            )
        with gr.Tab("Tokenizer"):
            input_text = gr.Textbox(lines=5, placeholder="Enter Hindi text here...")
            tokens = gr.Textbox(label="Token IDs", lines=5)
            highlighted_output = gr.HTML(label="Tokenized Text (Highlighted)")
            num_tokens_output = gr.Number(label="Number of Tokens")
            compression_ratio_output = gr.Text(label="Compression Ratio (vs UTF-8)")
            json_output = gr.Code(label="Token JSON", language="json")

            input_text.change(
                fn=gradio_interface,
                inputs=input_text,
                outputs=[tokens, highlighted_output, num_tokens_output, compression_ratio_output, json_output]
            )
            gr.Examples(
                sample_texts,
                inputs=input_text,
            )

        with gr.Tab("Decoder"):
            input_token_ids = gr.Textbox(lines=5, placeholder="Enter a list of token IDs (e.g., [1, 2, 3])")
            decoded_text_output = gr.Textbox(label="Decoded Text")
            input_token_ids.change(
                fn=decode_text,
                inputs=input_token_ids,
                outputs=[decoded_text_output]
            )

    iface.launch()