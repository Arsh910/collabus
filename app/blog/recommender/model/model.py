from transformers import AutoTokenizer
import torch
from collections import OrderedDict


class SentenceEncoder(torch.nn.Module):
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        super().__init__()
        from transformers import AutoModel

        self.model = AutoModel.from_pretrained(model_name)

    def forward(self, input_ids, attention_mask):
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        embeddings = outputs.last_hidden_state[:, 0]
        return embeddings


def load_device():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return device


def load_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    state_dict = torch.load(
        "blog/recommender/model/modelfiles/trained_model.pt", map_location=device
    )
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        new_key = k.replace("module.", "")
        new_state_dict[new_key] = v

    model = SentenceEncoder()
    model.load_state_dict(new_state_dict)
    model.to(device)
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    return model, tokenizer
