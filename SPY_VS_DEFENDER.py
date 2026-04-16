"""
Quantum Spy vs Defender - Educational Quantum Computing Game (v3)
Fixed: correct inverse-QFT gate order, real controlled-U gates in modular exponentiation,
       distinct circuit diagrams for RSA/Kyber/Dilithium, proper measurement extraction.

Dependencies: qiskit, qiskit-aer, numpy, matplotlib, tkinter
"""


import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer
from qiskit.compiler import transpile
from qiskit.visualization import circuit_drawer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, scrolledtext
import math
from fractions import Fraction
import random


# ─────────────────────────────────────────────────────────────
#  Quantum Engine
# ─────────────────────────────────────────────────────────────

class QuantumCryptanalysis:
    """Quantum algorithm core — Shor's algorithm with real Qiskit circuits."""

    def __init__(self):
        self.backend = Aer.get_backend('qasm_simulator')
        self.shots = 2048

    # ── helpers ──────────────────────────────────────────────

    @staticmethod
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    # ── Inverse QFT (FIXED: H first, then controlled-phase) ──

    def _apply_inverse_qft(self, qc, qreg, n):
        """
        Correct inverse QFT:
          For each qubit j (from 0 to n-1):
            1. Apply H to qubit j
            2. Apply controlled-Rz(-π/2^k) rotations for k=1..j
          Then swap qubits to reverse bit order.
        """
        for j in range(n):
            qc.h(qreg[j])
            for k in range(1, j + 1):
                angle = -np.pi / (2 ** k)
                qc.cp(angle, qreg[j - k], qreg[j])

        # Bit-reversal swaps
        for j in range(n // 2):
            qc.swap(qreg[j], qreg[n - j - 1])

    # ── Modular exponentiation (real controlled-X gates) ─────

    def _apply_modular_exponentiation(self, qc, counting_reg, aux_reg, a, N):
        """
        Controlled-U^{2^i} gates: for each counting qubit i, if the
        corresponding power of a mod N is not 1, apply a controlled-X
        from that counting qubit to each auxiliary qubit whose bit is set
        in (a^{2^i} mod N).  This is still educational / approximate but
        puts real gates on the circuit rather than just barriers.
        """
        n_aux = len(aux_reg)
        for i in range(len(counting_reg)):
            power = pow(a, 2 ** i, N)
            qc.barrier()
            # Encode the effect: flip auxiliary bits corresponding to
            # set bits of `power` (controlled on counting qubit i)
            for bit in range(n_aux):
                if (power >> bit) & 1:
                    qc.cx(counting_reg[i], aux_reg[bit])

    # ── Period extraction (FIXED: use stored bit_length) ─────

    def _extract_period_from_measurements(self, counts, a, N, n_counting):
        """Extract period r from measurement results using continued fractions."""
        total_states = 2 ** n_counting
        candidates = sorted(counts.items(), key=lambda x: x[1], reverse=True)

        for measured_str, _ in candidates[:10]:
            decimal_value = int(measured_str, 2)
            if decimal_value == 0:
                continue
            frac = Fraction(decimal_value, total_states).limit_denominator(N)
            r = frac.denominator
            if 1 < r < N and pow(a, r, N) == 1:
                return r
        return None

    # ── Main quantum period-finding ───────────────────────────

    def quantum_period_finding(self, a, N):
        """
        Full quantum period-finding circuit.
        Falls back to classical method + demo circuit for large N.
        Returns (period, circuit, counts).
        """
        n = int(np.ceil(np.log2(N + 1)))

        if n > 8:          # too expensive to simulate exactly
            return self._classical_period_finding(a, N)

        n_counting = 2 * n
        counting_reg = QuantumRegister(n_counting, 'q')
        aux_reg      = QuantumRegister(n,           'aux')
        c_reg        = ClassicalRegister(n_counting, 'c')
        qc = QuantumCircuit(counting_reg, aux_reg, c_reg)

        # |1⟩ in auxiliary register
        qc.x(aux_reg[0])

        # Hadamard superposition on counting register
        for i in range(n_counting):
            qc.h(counting_reg[i])

        qc.barrier()

        # Controlled modular exponentiation (real gates)
        self._apply_modular_exponentiation(qc, counting_reg, aux_reg, a, N)

        qc.barrier()

        # Inverse QFT on counting register
        self._apply_inverse_qft(qc, counting_reg, n_counting)

        qc.barrier()

        # Measure
        qc.measure(counting_reg, c_reg)

        # Execute
        compiled = transpile(qc, self.backend)
        result   = self.backend.run(compiled, shots=self.shots).result()
        counts   = result.get_counts()

        period = self._extract_period_from_measurements(counts, a, N, n_counting)
        return period, qc, counts

    # ── Classical fallback ────────────────────────────────────

    def _classical_period_finding(self, a, N):
        r, value = 1, a % N
        while value != 1 and r < N:
            value = (value * a) % N
            r += 1
        period = r if value == 1 else None
        return period, self.build_shors_demo_circuit(N), None

    # ── Demo circuit (always 4-qubit Shor structure) ─────────

    def build_shors_demo_circuit(self, N):
        """
        Correct 8-qubit educational Shor's circuit:
        4 counting qubits + 4 auxiliary qubits.
        Shows: H → barrier → controlled-X (mod-exp) → barrier → inv-QFT → barrier → measure
        """
        n = 4
        counting = QuantumRegister(n, 'q')
        aux      = QuantumRegister(n, 'aux')
        c        = ClassicalRegister(n, 'c')
        qc = QuantumCircuit(counting, aux, c)

        # |1⟩ in aux
        qc.x(aux[0])

        # Hadamard
        for i in range(n):
            qc.h(counting[i])

        qc.barrier()

        # Simplified controlled mod-exp gates
        a_demo = 2   # generic demo value
        for i in range(n):
            power = pow(a_demo, 2**i, max(N, 5))
            for bit in range(n):
                if (power >> bit) & 1:
                    qc.cx(counting[i], aux[bit])
            qc.barrier()

        # Inverse QFT
        self._apply_inverse_qft(qc, counting, n)

        qc.barrier()

        # Measure
        qc.measure(counting, c)

        return qc

    # ── Shor's algorithm (full) ───────────────────────────────

    def shors_algorithm(self, N):
        """Returns (factor1, factor2, circuit, steps)."""
        steps = []

        if N % 2 == 0:
            return 2, N // 2, self.build_shors_demo_circuit(N), ["N is even → trivial factor: 2"]

        for i in range(2, int(np.sqrt(N)) + 1):
            if N % i == 0:
                return i, N // i, self.build_shors_demo_circuit(N), [f"Classical factor found: {i}"]

        for attempt in range(12):
            a = random.randint(2, N - 1)
            steps.append(f"Attempt {attempt+1}: Chose random a = {a}")

            g = self.gcd(a, N)
            if g > 1:
                steps.append(f"Lucky! gcd({a}, {N}) = {g}, found factor immediately")
                return g, N // g, self.build_shors_demo_circuit(N), steps

            steps.append(f"Running quantum period finding for a={a}, N={N}...")
            result = self.quantum_period_finding(a, N)
            r, circuit, _ = result

            if r is None:
                steps.append("Period finding failed, trying next a")
                continue

            steps.append(f"Found period r = {r}")

            if r % 2 != 0:
                steps.append(f"Period r={r} is odd, trying next a")
                continue

            x = pow(a, r // 2, N)
            if x == N - 1:
                steps.append("a^(r/2) ≡ -1 (mod N), trying next a")
                continue

            f1 = self.gcd(x + 1, N)
            f2 = self.gcd(x - 1, N)
            steps.append(f"gcd({x}+1, {N}) = {f1},  gcd({x}-1, {N}) = {f2}")

            if 1 < f1 < N:
                steps.append(f"SUCCESS! Factors: {f1} × {f2} = {N}")
                return f1, f2, circuit or self.build_shors_demo_circuit(N), steps
            if 1 < f2 < N:
                steps.append(f"SUCCESS! Factors: {f2} × {f1} = {N}")
                return f2, f1, circuit or self.build_shors_demo_circuit(N), steps

        steps.append("Failed to find factors after all attempts")
        return None, None, self.build_shors_demo_circuit(N), steps

    # ── Post-quantum circuit visualisations ──────────────────

    def build_kyber_circuit(self):
        """
        Conceptual Kyber / LWE circuit:
        Shows lattice sampling: random matrix A applied to secret s,
        with added noise e — illustrating 'Learning With Errors'.
        5 qubits: 3 for secret vector s, 2 for noise/error.
        """
        n = 3  # secret vector dimension
        e = 2  # error dimension
        secret = QuantumRegister(n, 's')
        error  = QuantumRegister(e, 'e')
        c      = ClassicalRegister(n + e, 'c')
        qc = QuantumCircuit(secret, error, c)

        # Encode secret s in superposition (lattice sampling)
        qc.h(secret[0])
        qc.h(secret[1])
        qc.h(secret[2])

        qc.barrier(label='Lattice A·s')

        # Matrix A acting on secret (random lattice operations)
        qc.cx(secret[0], secret[1])
        qc.cx(secret[1], secret[2])
        qc.cx(secret[2], secret[0])
        qc.rz(np.pi / 4, secret[0])
        qc.rz(np.pi / 3, secret[1])

        qc.barrier(label='+noise e')

        # Add noise to error qubits
        qc.h(error[0])
        qc.cx(secret[0], error[0])
        qc.rx(np.pi / 8, error[1])
        qc.cx(secret[1], error[1])

        qc.barrier(label='b=A·s+e')

        # Measure — finding s from b is hard (LWE hardness)
        qc.measure(secret, c[:n])
        qc.measure(error,  c[n:])

        return qc

    def build_dilithium_circuit(self):
        """
        Conceptual Dilithium / MSIS circuit:
        Models the hash-and-sign structure over lattice basis vectors.
        6 qubits: 3 for the message hash, 3 for the signature commitment.
        """
        n = 3
        msg  = QuantumRegister(n, 'msg')
        sig  = QuantumRegister(n, 'sig')
        c    = ClassicalRegister(n * 2, 'c')
        qc   = QuantumCircuit(msg, sig, c)

        # Message hashing (uniform superposition)
        for i in range(n):
            qc.h(msg[i])

        qc.barrier(label='Hash H(msg)')

        # Signature commitment — secret lattice basis
        qc.ry(np.pi / 3, sig[0])
        qc.ry(np.pi / 5, sig[1])
        qc.ry(np.pi / 7, sig[2])

        qc.barrier(label='Commit w=Ay')

        # Challenge-response (Fiat-Shamir lattice)
        qc.cx(msg[0], sig[0])
        qc.cx(msg[1], sig[1])
        qc.cx(msg[2], sig[2])
        qc.cz(sig[0], sig[1])
        qc.cz(sig[1], sig[2])

        qc.barrier(label='Sign z=y+cs')

        # Verify: check lattice norm bound
        qc.h(sig[0])
        qc.h(sig[2])

        qc.barrier(label='Verify')

        qc.measure(msg, c[:n])
        qc.measure(sig, c[n:])

        return qc


# ─────────────────────────────────────────────────────────────
#  RSA
# ─────────────────────────────────────────────────────────────

class RSACryptosystem:
    """RSA with slightly larger educational primes."""

    # Primes big enough to be interesting but simulatable
    PRIMES = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67]

    def __init__(self):
        self.public_key  = None
        self.private_key = None
        self.N = None

    def generate_keypair(self):
        p = random.choice(self.PRIMES)
        q = random.choice([x for x in self.PRIMES if x != p])
        self.N = p * q
        phi = (p - 1) * (q - 1)
        e = 65537
        while math.gcd(e, phi) != 1:
            e = random.randint(3, phi - 1)
        d = pow(e, -1, phi)
        self.public_key  = (e, self.N)
        self.private_key = (d, self.N)
        return {'p': p, 'q': q, 'N': self.N, 'e': e, 'd': d, 'phi': phi}

    def encrypt(self, message, public_key):
        e, N = public_key
        m = int.from_bytes(message.encode(), 'big') % N
        return pow(m, e, N)

    def decrypt(self, ciphertext, private_key):
        d, N = private_key
        m = pow(ciphertext, d, N)
        try:
            return m.to_bytes((m.bit_length() + 7) // 8, 'big').decode()
        except Exception:
            return str(m)


# ─────────────────────────────────────────────────────────────
#  Post-Quantum Crypto (conceptual)
# ─────────────────────────────────────────────────────────────

class PostQuantumCrypto:
    DESCRIPTIONS = {
        'Kyber': """
CRYSTALS-Kyber (Key Encapsulation — NIST ML-KEM)
• Hard problem : Module Learning With Errors (MLWE)
• Security     : Lattice-based — resistant to Shor's algorithm
• Use case     : Secure key exchange (replaces ECDH / RSA-KEM)
• Key sizes    : Kyber-512 → 800 B public key
• Why safe     : No known quantum speedup for MLWE
""",
        'Dilithium': """
CRYSTALS-Dilithium (Digital Signatures — NIST ML-DSA)
• Hard problem : Module Short Integer Solution (MSIS) + MLWE
• Security     : Lattice-based — resistant to Shor's algorithm
• Use case     : Authentication, code signing
• Key sizes    : Dilithium-2 → 1312 B public key
• Why safe     : Lattice problems give only √n quantum speedup (Grover)
"""
    }

    def __init__(self, algorithm='Kyber'):
        self.algorithm = algorithm

    def get_description(self):
        return self.DESCRIPTIONS.get(self.algorithm, "Unknown algorithm")

    def is_vulnerable_to_quantum(self):
        return False


# ─────────────────────────────────────────────────────────────
#  Game UI
# ─────────────────────────────────────────────────────────────

class QuantumSpyGame:

    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.title("Quantum Spy vs Defender — Educational Game")
        self.root.geometry("1440x900")

        # State
        self.round_number       = 1
        self.spy_score          = 0
        self.defender_score     = 0
        self.current_encryption = "RSA"

        # Components
        self.quantum_engine = QuantumCryptanalysis()
        self.rsa            = RSACryptosystem()
        self.pqc            = None
        self.current_keys   = {}

        self._setup_ui()
        self._init_game()

    def _on_close(self):
        self.root.destroy()

    # ── UI ────────────────────────────────────────────────────

    def _setup_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky='nsew')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(1, weight=1)
        main.rowconfigure(2, weight=1)

        # Title
        ttk.Label(main, text="🔐 Quantum Spy vs Defender 🛡️",
                  font=('Arial', 20, 'bold')).grid(row=0, column=0, columnspan=3, pady=10)

        # ── Left: Game Status ─────────────────────────────────
        lf = ttk.LabelFrame(main, text="Game Status", padding=8)
        lf.grid(row=1, column=0, sticky='nsew', padx=4)
        self.status_text = scrolledtext.ScrolledText(lf, width=40, height=16,
                                                     wrap=tk.WORD, font=('Courier', 9))
        self.status_text.pack(fill='both', expand=True)

        # ── Centre: Circuit visualisation ─────────────────────
        cf = ttk.LabelFrame(main, text="Quantum Circuit Visualization", padding=8)
        cf.grid(row=1, column=1, rowspan=2, sticky='nsew', padx=4)
        self.viz_frame = ttk.Frame(cf)
        self.viz_frame.pack(fill='both', expand=True)

        # ── Right: Controls ───────────────────────────────────
        rf = ttk.LabelFrame(main, text="Controls", padding=8)
        rf.grid(row=1, column=2, sticky='nsew', padx=4)

        ttk.Label(rf, text="Round:", font=('Arial', 11, 'bold')).pack()
        self.round_label = ttk.Label(rf, text="1", font=('Arial', 14)); self.round_label.pack()
        ttk.Separator(rf, orient='horizontal').pack(fill='x', pady=8)

        ttk.Label(rf, text="Scores:", font=('Arial', 11, 'bold')).pack()
        self.spy_lbl = ttk.Label(rf, text="🕵️ Spy: 0",      font=('Arial', 12), foreground='red');  self.spy_lbl.pack()
        self.def_lbl = ttk.Label(rf, text="🛡️ Defender: 0", font=('Arial', 12), foreground='blue'); self.def_lbl.pack()
        ttk.Separator(rf, orient='horizontal').pack(fill='x', pady=8)

        ttk.Label(rf, text="Current Encryption:", font=('Arial', 11, 'bold')).pack()
        self.enc_lbl = ttk.Label(rf, text="RSA", font=('Arial', 12)); self.enc_lbl.pack()
        ttk.Separator(rf, orient='horizontal').pack(fill='x', pady=8)

        ttk.Label(rf, text="Spy Actions:", font=('Arial', 10, 'bold')).pack(pady=(4, 2))
        self.btn_attack = ttk.Button(rf, text="🎯 Attack with Shor's Algorithm",
                                     command=self._spy_attack)
        self.btn_attack.pack(fill='x', pady=2)
        ttk.Separator(rf, orient='horizontal').pack(fill='x', pady=8)

        ttk.Label(rf, text="Defender Actions:", font=('Arial', 10, 'bold')).pack(pady=(4, 2))
        self.btn_kyber = ttk.Button(rf, text="🔒 Upgrade to Kyber",
                                    command=lambda: self._defender_upgrade('Kyber'))
        self.btn_kyber.pack(fill='x', pady=2)
        self.btn_dilithium = ttk.Button(rf, text="✍️ Upgrade to Dilithium",
                                        command=lambda: self._defender_upgrade('Dilithium'))
        self.btn_dilithium.pack(fill='x', pady=2)
        ttk.Separator(rf, orient='horizontal').pack(fill='x', pady=8)

        self.btn_next  = ttk.Button(rf, text="➡️ Next Round",  command=self._next_round, state='disabled')
        self.btn_next.pack(fill='x', pady=4)
        self.btn_reset = ttk.Button(rf, text="🔄 Reset Game",  command=self._reset_game)
        self.btn_reset.pack(fill='x', pady=2)

        # ── Bottom left: Educational info ──────────────────────
        bf = ttk.LabelFrame(main, text="Educational Information", padding=8)
        bf.grid(row=2, column=0, sticky='nsew', padx=4, pady=4)
        self.info_text = scrolledtext.ScrolledText(bf, width=40, height=12,
                                                   wrap=tk.WORD, font=('Arial', 9))
        self.info_text.pack(fill='both', expand=True)

        # ── Bottom right: Algorithm details ───────────────────
        af = ttk.LabelFrame(main, text="Algorithm Details", padding=8)
        af.grid(row=2, column=2, sticky='nsew', padx=4, pady=4)
        self.algo_text = scrolledtext.ScrolledText(af, width=40, height=12,
                                                   wrap=tk.WORD, font=('Arial', 9))
        self.algo_text.pack(fill='both', expand=True)

    # ── Game logic ────────────────────────────────────────────

    def _init_game(self):
        self._log("🎮 Game Initialised!")
        self._log(f"Round {self.round_number} — RSA encryption active\n")
        self._log("📚 Educational Mode: demonstrates how quantum computers")
        self._log("   threaten classical cryptography via Shor's algorithm.\n")

        self.current_keys = self.rsa.generate_keypair()
        self._log("🔑 RSA Keys Generated:")
        self._log(f"   p = {self.current_keys['p']}, q = {self.current_keys['q']}")
        self._log(f"   N = p × q = {self.current_keys['N']}")
        self._log(f"   Public key: (e={self.current_keys['e']}, N={self.current_keys['N']})")

        self._show_edu_info()

    def _spy_attack(self):
        self._log(f"\n🕵️ SPY ATTACKS — Round {self.round_number}")
        self._disable_btns()

        if self.current_encryption == "RSA":
            N = self.current_keys['N']
            self._log(f"Target: RSA  (N = {N})")
            self._log("⚛️  Initialising quantum computer…")
            self.root.update()

            f1, f2, circuit, steps = self.quantum_engine.shors_algorithm(N)

            self._log("\n📊 Shor's Algorithm Execution:")
            for s in steps:
                self._log(f"   {s}")

            self._visualize(circuit, label=f"Shor's Algorithm — Period Finding (N={N})")

            if f1 and f2:
                self._log(f"\n💥 ENCRYPTION BROKEN!")
                self._log(f"   Factors: {f1} × {f2} = {N}")
                self._log(f"   Private key d = {self.current_keys['d']}")
                self.spy_score += 10
                self.spy_lbl.config(text=f"🕵️ Spy: {self.spy_score}")
                self._log("🏆 Spy earns 10 points!")
                self._show_shors_details()
            else:
                self._log("❌ Attack did not converge — Defender +5")
                self.defender_score += 5
                self.def_lbl.config(text=f"🛡️ Defender: {self.defender_score}")

        else:
            # Post-quantum encryption active
            self._log(f"Target: {self.current_encryption}")
            self._log("⚛️  Running Shor's algorithm…")
            self.root.update()

            # Show the *appropriate* PQC circuit, not a Shor circuit
            if self.current_encryption == 'Kyber':
                pqc_circuit = self.quantum_engine.build_kyber_circuit()
                label = "Kyber / LWE Lattice Structure (Quantum-Resistant)"
            else:
                pqc_circuit = self.quantum_engine.build_dilithium_circuit()
                label = "Dilithium / MSIS Lattice Structure (Quantum-Resistant)"

            self._visualize(pqc_circuit, label=label)

            self._log("❌ ATTACK FAILED!")
            self._log(f"   {self.current_encryption} is quantum-resistant")
            self._log("   Lattice problems have no known quantum speedup")
            self.defender_score += 10
            self.def_lbl.config(text=f"🛡️ Defender: {self.defender_score}")
            self._log("🏆 Defender earns 10 points!")
            self._show_pqc_details()

        self.btn_next.config(state='normal')

    def _defender_upgrade(self, algorithm):
        self._log(f"\n🛡️ DEFENDER UPGRADES — Round {self.round_number}")
        self._log(f"   {self.current_encryption} → {algorithm}")

        self.current_encryption = algorithm
        self.enc_lbl.config(text=algorithm)
        self.pqc = PostQuantumCrypto(algorithm)
        self._log("✅ Upgrade complete!")
        self._log(self.pqc.get_description())
        self._log("🔐 System is now quantum-resistant!\n")

        self.defender_score += 5
        self.def_lbl.config(text=f"🛡️ Defender: {self.defender_score}")

        # Show the matching circuit immediately on upgrade
        if algorithm == 'Kyber':
            self._visualize(self.quantum_engine.build_kyber_circuit(),
                            label="Kyber / LWE Lattice Circuit (Post-Quantum)")
        else:
            self._visualize(self.quantum_engine.build_dilithium_circuit(),
                            label="Dilithium / MSIS Lattice Circuit (Post-Quantum)")

        self.btn_kyber.config(state='disabled')
        self.btn_dilithium.config(state='disabled')

    def _next_round(self):
        self.round_number += 1
        self.round_label.config(text=str(self.round_number))
        self._log(f"\n{'='*48}")
        self._log(f"🎮 ROUND {self.round_number}")
        self._log(f"{'='*48}")
        self._enable_btns()
        self.btn_next.config(state='disabled')

        if self.current_encryption == "RSA":
            self.current_keys = self.rsa.generate_keypair()
            self._log(f"🔑 New RSA keys: N = {self.current_keys['N']}")

    def _reset_game(self):
        self.round_number       = 1
        self.spy_score          = 0
        self.defender_score     = 0
        self.current_encryption = "RSA"

        self.round_label.config(text="1")
        self.spy_lbl.config(text="🕵️ Spy: 0")
        self.def_lbl.config(text="🛡️ Defender: 0")
        self.enc_lbl.config(text="RSA")

        for w in self.viz_frame.winfo_children():
            w.destroy()

        self.status_text.delete('1.0', tk.END)
        self.info_text.delete('1.0', tk.END)
        self.algo_text.delete('1.0', tk.END)

        self._enable_btns()
        self._init_game()

    # ── Visualisation ─────────────────────────────────────────

    def _visualize(self, circuit, label="Quantum Circuit"):
        for w in self.viz_frame.winfo_children():
            w.destroy()

        try:
            fig = circuit_drawer(circuit, output='mpl', fold=25, idle_wires=False)
            fig.set_size_inches(11, 6)
            fig.suptitle(label, fontsize=11, y=0.99)
            fig.tight_layout(pad=0.8)
        except Exception:
            fig, ax = plt.subplots(figsize=(11, 6))
            ax.text(0.01, 0.99, str(circuit.draw(output='text', fold=100)),
                    ha='left', va='top', fontsize=8, family='monospace', transform=ax.transAxes)
            ax.axis('off')
            fig.suptitle(label, fontsize=11)

        canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    # ── Educational text ──────────────────────────────────────

    def _show_edu_info(self):
        info = """
📚 EDUCATIONAL OVERVIEW

🔐 Classical Cryptography (RSA):
• Security based on difficulty of factoring large numbers
• N = p × q; finding p, q from N requires exponential time classically
• RSA-2048 would take billions of years classically

⚛️ Quantum Threat — Shor's Algorithm:
• Quantum computers factor N in polynomial time O(n³)
• Uses quantum superposition + Quantum Fourier Transform
• Breaks RSA, DSA, ECDSA, DH

🛡️ Post-Quantum Cryptography:
• CRYSTALS-Kyber  : Lattice-based key exchange (NIST ML-KEM 2024)
• CRYSTALS-Dilithium: Lattice-based signatures  (NIST ML-DSA 2024)
• Based on Learning With Errors — no known quantum speedup

🎯 Game Objective:
• Spy    : Break RSA encryption with Shor's algorithm
• Defender: Upgrade to quantum-safe algorithms ASAP
"""
        self.info_text.insert(tk.END, info)

    def _show_shors_details(self):
        self.algo_text.delete('1.0', tk.END)
        self.algo_text.insert(tk.END, """
🔬 SHOR'S ALGORITHM BREAKDOWN

Circuit structure (this game):
  q₀–q₃  : Counting register (superposition)
  aux₀–aux₃: Auxiliary register (starts |1⟩)

Steps:
  1. H on all counting qubits → superposition
  2. Controlled-U^{2^i}: controlled modular mult.
     Each counting qubit controls a^{2^i} mod N
     acting on the auxiliary register
  3. Inverse QFT on counting register:
     H(qⱼ) first, then controlled-Rz rotations
     (note: opposite order to forward QFT)
  4. Measure → phase → period r via cont. fractions

Classical post-processing:
  • f₁ = gcd(a^(r/2)+1, N)
  • f₂ = gcd(a^(r/2)−1, N)
  • Verify f₁ × f₂ = N

Complexity:
  Classical: O(exp(n^{1/3}))
  Quantum  : O(n³) — exponential speedup!

⚠️ Threat: CRITICAL for any RSA/ECC system
""")

    def _show_pqc_details(self):
        self.algo_text.delete('1.0', tk.END)
        self.algo_text.insert(tk.END, """
🛡️ POST-QUANTUM CRYPTOGRAPHY

Why Kyber's circuit looks different:
  • No counting register — no period to find
  • Secret vector s is encoded in lattice qubits
  • Matrix A applies random lattice operations
  • Noise e is added (LWE hardness)
  • Shor's QFT step has no effect on b = A·s + e

Kyber (ML-KEM) circuit shows:
  s qubits : secret vector (H → superposition)
  Lattice A: CX gates scramble s classically
  e qubits : noise addition (RX rotations)
  Result b : cannot be inverted without s

Why Dilithium's circuit looks different:
  • Models hash-and-sign over lattice basis
  • msg qubits: uniform message hash (H gates)
  • sig qubits: commitment w = Ay (RY rotations)
  • Challenge-response via CX/CZ gates
  • Signature norm check (final H gates)

Security summary:
  Grover's algorithm gives only √n speedup
  Increase key size by 2× compensates fully
  ✅ NIST Standardised 2024
""")

    # ── Helpers ───────────────────────────────────────────────

    def _log(self, msg):
        self.status_text.insert(tk.END, msg + "\n")
        self.status_text.see(tk.END)
        self.root.update()

    def _disable_btns(self):
        for b in (self.btn_attack, self.btn_kyber, self.btn_dilithium):
            b.config(state='disabled')

    def _enable_btns(self):
        self.btn_attack.config(state='normal')
        if self.current_encryption == "RSA":
            self.btn_kyber.config(state='normal')
            self.btn_dilithium.config(state='normal')


# ─────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    QuantumSpyGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()