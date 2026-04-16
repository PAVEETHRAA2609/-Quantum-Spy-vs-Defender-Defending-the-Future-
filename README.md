# -Quantum-Spy-vs-Defender-Defending-the-Future-
An interactive educational game that demonstrates how quantum computing threatens classical cryptography and how post-quantum algorithms defend against it.

---

## 📌 Project Overview

**Quantum Spy vs Defender** is a simulation-based project that helps users understand:

* Why RSA encryption is vulnerable to quantum attacks
* How **Shor’s Algorithm** can break encryption
* How modern **post-quantum cryptography** (Kyber & Dilithium) protects data

The project turns complex quantum concepts into a **game-like experience**, where users play as both:

* 🕵️ **Spy (Attacker)** – Breaks encryption using quantum algorithms
* 🛡️ **Defender** – Upgrades security using quantum-resistant techniques

---

## 🎯 Objectives

* Demonstrate real-world risks of quantum computing on encryption
* Visualize quantum circuits using Qiskit
* Compare classical vs post-quantum cryptography
* Make learning interactive and easy to understand

---

## ⚙️ Technologies Used

* **Python** – Core programming
* **Qiskit** – Quantum circuit simulation
* **Tkinter** – Graphical User Interface
* **Matplotlib** – Circuit visualization

---

## 🧠 Key Concepts Covered

* RSA Encryption
* Shor’s Algorithm
* Quantum Fourier Transform (QFT)
* Learning With Errors (LWE)
* Lattice-based Cryptography
* Post-Quantum Cryptography

---

## 🔄 How It Works

### 1️⃣ Initialization

* RSA keys are generated using two prime numbers
* Public and private keys are created

### 2️⃣ Attack Phase (Spy)

* Shor’s Algorithm is executed using a quantum circuit
* Period finding is performed using QFT
* RSA key is broken

### 3️⃣ Defense Phase

* System is upgraded to:

  * **Kyber** (encryption)
  * **Dilithium** (digital signature)

### 4️⃣ Re-Attack

* Spy attempts attack again
* Attack fails due to quantum-resistant algorithms

---

## 🔐 Algorithms Used

### 🔸 RSA (Classical Cryptography)

* Based on integer factorization
* Vulnerable to quantum attacks

### 🔸 Shor’s Algorithm

* Quantum algorithm for factorization
* Breaks RSA efficiently

### 🔸 Kyber

* Based on Learning With Errors (LWE)
* Resistant to quantum attacks

### 🔸 Dilithium

* Lattice-based digital signature scheme
* Ensures authentication and integrity

---

## 📊 Features

* Interactive GUI-based simulation
* Real quantum circuit visualization
* Educational step-by-step output
* Game-like scoring system
* Comparison between algorithms

---


---

## 🚀 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/quantum-spy-defender.git

# Navigate to project folder
cd quantum-spy-defender

# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the project
python main.py
```

---

## 📚 References

* Shor, P. W. (1994) – Quantum Factorization
* Regev, O. (2005) – Learning With Errors
* NIST (2024) – Post-Quantum Cryptography
* Qiskit Documentation – IBM Quantum

---

## 🌍 Real-World Relevance

* Banks and secure systems rely on RSA today
* Quantum computers can break RSA in the future
* Organizations are transitioning to post-quantum cryptography

---



## ⭐ Future Enhancements

* Real quantum hardware execution (IBM Quantum)
* More post-quantum algorithms
* Web-based version
* Multiplayer simulation

---

## 📌 Conclusion

This project demonstrates the urgent need to move from classical encryption to quantum-resistant systems by providing a hands-on, visual learning experience.

---
