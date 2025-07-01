# 🐤 Flappy Bird AI using NEAT

This project implements an AI that learns to play **Flappy Bird** using **NEAT (NeuroEvolution of Augmenting Topologies)**. Over generations, the AI improves its performance through evolving neural networks.

Train your own AI birds and watch them learn to survive through pipes!

---

## 🧠 How It Works

- The **NEAT-Python** library is used to evolve a population of neural networks.
- Each bird is controlled by a neural network that takes in game state data and outputs a decision (flap or not).
- Fitness is determined by survival time or distance traveled.
- Over generations, the birds evolve better strategies to fly through pipes.

---

## 🎮 Features

- ✅ AI learns from scratch using evolution
- 📊 Visual display of fitness and scores
- 🧠 NEAT configuration easily customizable
- 💥 Collision detection, scoring, and smooth physics
- 🎯 Real-time training visualization

---

## 🚀 How to Run

### 1. Clone the Repository
```bash
git clone https://github.com/ChinmayBansal010/Flappy-AI
cd Flappy-AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Training the AI
```bash
python main.py
```

---

## 📂 Folder Structure

```
Flappy-AI/
├── main.py                # Main game logic and NEAT integration
├── bird.py                # Bird behavior and physics
├── pipe.py                # Pipe movement and collision
├── base.py                # Base platform logic
├── neat-config.txt        # NEAT configuration
├── assets/                # Game images (bird, background, etc.)
```

---

## 📸 Screenshots

*(Add training visuals or a gif of AI playing Flappy Bird here)*

---

## 📄 License

This project is intended for **educational and research** use only.  
Reusing or adapting code requires proper attribution and **written permission** for commercial or full-software use.

---

## 👨‍💻 Author

**Chinmay Bansal**  
📧 chinmay8521@gmail.com  
🔗 GitHub: [@ChinmayBansal010](https://github.com/ChinmayBansal010)

---

## 🌟 Contributions

Open to feedback and improvements.  
Feel free to fork, star, and open issues or pull requests!
