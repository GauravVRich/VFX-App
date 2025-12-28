import torch
from diffusers import AutoencoderKL
from PIL import Image
import numpy as np
from torchvision import transforms

class TweenEngine:
    def __init__(self):
        # Using a lightweight VAE for latent manipulations
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse").to(self.device)
        self.preprocess = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])

    def slerp(self, t, v0, v1, DOT_THRESHOLD=0.9995):
        """Spherical linear interpolation for latent vectors."""
        v0_norm = v0 / torch.norm(v0)
        v1_norm = v1 / torch.norm(v1)
        dot = torch.sum(v0_norm * v1_norm)
        
        if torch.abs(dot) > DOT_THRESHOLD:
            return (1 - t) * v0 + t * v1
        
        theta_0 = torch.acos(dot)
        theta_t = theta_0 * t
        sin_theta_0 = torch.sin(theta_0)
        sin_theta_t = torch.sin(theta_t)
        
        s0 = torch.sin(theta_0 - theta_t) / sin_theta_0
        s1 = sin_theta_t / sin_theta_0
        return s0 * v0 + s1 * v1

    def generate_tween(self, img_a_path, img_b_path, num_frames=12):
        img_a = self.preprocess(Image.open(img_a_path).convert("RGB")).unsqueeze(0).to(self.device)
        img_b = self.preprocess(Image.open(img_b_path).convert("RGB")).unsqueeze(0).to(self.device)

        with torch.no_grad():
            # Encode images to Latent Space
            latent_a = self.vae.encode(img_a).latent_dist.sample()
            latent_b = self.vae.encode(img_b).latent_dist.sample()

            frames = []
            for i in range(num_frames):
                t = i / (num_frames - 1)
                # Interpolate in Latent Space
                interp_latent = self.slerp(t, latent_a, latent_b)
                
                # Decode Latent back to Image
                decoded = self.vae.decode(interp_latent).sample
                decoded = (decoded / 2 + 0.5).clamp(0, 1)
                decoded = decoded.cpu().permute(0, 2, 3, 1).numpy()[0]
                frames.append(Image.fromarray((decoded * 255).astype(np.uint8)))
        
        return frames