import torch.nn as nn
import torch
class Embedding(nn.Module):
    # input: image(2d)
    # output: patches(1d)
    def __init__(self, patch_size, embedding_dim):
        super().__init__()
        # should break image, apply linea and then flatten 
        # a conv layer with kernel size = patch_size and stride = patch_size will do exactly that
        self.patcher = nn.Conv2d(
            in_channels=3, out_channels=embedding_dim, kernel_size=patch_size, stride=patch_size
        )
    def forward(self, x):
        # x (B, 3, H, W)

        x = self.patcher(x)  
        # (B, embedding_dim, H/patch_size, W/patch_size)

        x = x.flatten(2)  # (B, embedding_dim, N_patches)
        # (B, embedding_dim, N_patches)

        x = x.transpose(1, 2)  
        # (B, N_patches, embedding_dim)

        return x


class MultiheadAttention(nn.Module):
    def __init__(self, embedding_dim, num_heads):
        assert embedding_dim % num_heads == 0

        super().__init__()
        self.embedding_dim = embedding_dim
        self.head_dim = embedding_dim // num_heads
        self.num_heads = num_heads


        # qkv dim is (B, heads, N_patches, head_dim)
        # self.k_linear = nn.Linear(embedding_dim, embedding_dim)
        # self.q_linear = nn.Linear(embedding_dim, embedding_dim)
        # self.v_linear = nn.Linear(embedding_dim, embedding_dim)
        self.kqv_linear = nn.Linear(embedding_dim, embedding_dim * 3)
        # merging the k, q and v is inspired by AI
        self.linear = nn.Linear(embedding_dim, embedding_dim)


    def forward(self, x):
        # x (B, N_patches, embedding_dim)
        B, N, _ = x.shape

        kqv = self.kqv_linear(x)  
        # (B, N_patches, 3 * embedding_dim)

        kqv = kqv.reshape(B, N, 3, self.num_heads, self.head_dim)
        # (B, N_patches, 3, num_heads, head_dim)

        kqv = kqv.permute(2, 0, 3, 1, 4)
        # (3, B, num_heads, N_patches, head_dim)
        k = kqv[0]  # (B, num_heads, n_patches, head_dim)
        q = kqv[1]  # (B, num_heads, N_patches, head_dim)
        v = kqv[2]  # (B, num_heads, N_patches, head_dim)

        # A = softmax( (Q @ K.T) / sqrt(d_k) ) @ V
        attn = (q @ k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        attn = attn.softmax(dim=-1)  
        try:
            self.last_attn = attn.detach()
        except Exception:
            self.last_attn = attn
        
        out = attn @ v  
        out = out.transpose(1, 2).reshape(B, N, self.embedding_dim)
        out = self.linear(out)

        return out

class MLP(nn.Module):
    def __init__(self, embedding_dim, hidden_dim):
        super().__init__()

        self.mlp = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, embedding_dim)
        )

    def forward(self, x):
        return self.mlp(x)

class TransfomerEncode(nn.Module):
    def __init__(self, embedding_dim, num_heads, mlp_hidden_dim):
        super().__init__()
        self.mha = MultiheadAttention(embedding_dim, num_heads)
        self.mlp = MLP(embedding_dim, mlp_hidden_dim)
        self.norm1 = nn.LayerNorm(embedding_dim)
        self.norm2 = nn.LayerNorm(embedding_dim)

    def forward(self, x):
        mha = self.mha(self.norm1(x))  
        out = x + mha  
        out = out + self.mlp(self.norm2(out))
        return out

class ViT(nn.Module):
    def __init__(self, image_size, patch_size, embedding_dim, num_heads, num_layers, num_classes, mlp_hidden_dim=None):
        super().__init__()
        if mlp_hidden_dim is None:
            mlp_hidden_dim = embedding_dim * 4
        num_patches = (image_size // patch_size) ** 2
        self.embedding = Embedding(patch_size, embedding_dim)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embedding_dim))
        self.pos_embedding = nn.Parameter(torch.zeros(
            1, num_patches + 1, embedding_dim
        ))
        self.layers = nn.ModuleList([
            TransfomerEncode(embedding_dim, num_heads, mlp_hidden_dim)
            for _ in range(num_layers)
        ])
        self.classifier = nn.Sequential(
            nn.LayerNorm(embedding_dim),
            nn.Linear(embedding_dim, num_classes)
        )
    def forward(self, x):
        x = self.embedding(x)  
        B, N, *_ = x.shape
        cls_tokens = self.cls_token.expand(B, -1, -1)  
        x = torch.cat((cls_tokens, x), dim=1)  
        x = x + self.pos_embedding  
        for layer in self.layers:
            x = layer(x)
        x = x[:, 0]  
        x = self.classifier(x)
        return x