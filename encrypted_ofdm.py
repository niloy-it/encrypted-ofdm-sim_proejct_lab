"""
╔═══════════════════════════════════════════════════════════════════╗
║             ENCRYPTED-OFDM SIMULATION                             ║
║                                                                   ║
║  Based on: Mohammed & Saha, "Encrypted-OFDM: A Secured           ║
║            Wireless Waveform," Elsevier Computer Networks, 2024   ║
║                                                                   ║
║  Author: Niloy Saha (niloyete@gmail.com)                         ║
║  Date: January 2025                                               ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List
import os

# Create results directory if not exists
os.makedirs('results', exist_ok=True)


class EncryptedOFDM:
    """
    Encrypted-OFDM System Implementation
    
    This class implements the two-stage encryption process:
    1. Time-domain randomization (sample permutation)
    2. Phase distortion (key-derived phase rotation)
    """
    
    def __init__(self, N: int = 64, cp_ratio: float = 0.25):
        """
        Initialize the Encrypted-OFDM system.
        
        Args:
            N: Number of subcarriers (default: 64)
            cp_ratio: Cyclic prefix ratio (default: 0.25)
        """
        self.N = N
        self.cp_len = int(N * cp_ratio)
        print(f"[INIT] Encrypted-OFDM System")
        print(f"       Subcarriers: {N}, CP Length: {self.cp_len}")
    
    def generate_bits(self, num_bits: int) -> np.ndarray:
        """Generate random binary data."""
        return np.random.randint(0, 2, num_bits)
    
    def bpsk_modulate(self, bits: np.ndarray) -> np.ndarray:
        """BPSK Modulation: 0 → -1, 1 → +1"""
        return 2 * bits - 1
    
    def bpsk_demodulate(self, symbols: np.ndarray) -> np.ndarray:
        """BPSK Demodulation: Threshold at 0"""
        return (np.real(symbols) > 0).astype(int)
    
    def generate_ofdm_symbol(self, data_symbols: np.ndarray) -> np.ndarray:
        """
        Generate standard OFDM symbol.
        
        Process:
        1. Map data to subcarriers
        2. IFFT to time domain
        3. Add cyclic prefix
        """
        # Ensure correct length
        if len(data_symbols) < self.N:
            padded = np.zeros(self.N, dtype=complex)
            padded[:len(data_symbols)] = data_symbols
        else:
            padded = data_symbols[:self.N]
        
        # IFFT: Frequency → Time domain
        time_domain = np.fft.ifft(padded, self.N)
        
        # Add cyclic prefix
        ofdm_symbol = np.concatenate([
            time_domain[-self.cp_len:],
            time_domain
        ])
        
        return ofdm_symbol
    
    def encrypt_symbol(self, ofdm_symbol: np.ndarray, key: int) -> np.ndarray:
        """
        Apply Encrypted-OFDM transformation.
        
        Stage 1 - Randomization:
            Permute time-domain samples using key-derived order
            
        Stage 2 - Phase Distortion:
            Apply key-derived phase rotations to each sample
        """
        # Remove CP for encryption
        symbol_no_cp = ofdm_symbol[self.cp_len:]
        
        # STAGE 1: TIME-DOMAIN RANDOMIZATION
        np.random.seed(key)
        permutation = np.random.permutation(self.N)
        randomized = symbol_no_cp[permutation]
        
        # STAGE 2: PHASE DISTORTION
        np.random.seed(key + 12345)
        phase_indices = np.random.randint(0, self.N, self.N)
        phase_values = np.exp(2j * np.pi * phase_indices / self.N)
        encrypted = randomized * phase_values
        
        # Re-add cyclic prefix
        encrypted_with_cp = np.concatenate([
            encrypted[-self.cp_len:],
            encrypted
        ])
        
        return encrypted_with_cp
    
    def decrypt_symbol(self, encrypted_symbol: np.ndarray, key: int) -> np.ndarray:
        """
        Decrypt Encrypted-OFDM symbol (legitimate receiver with key).
        """
        # Remove CP
        symbol_no_cp = encrypted_symbol[self.cp_len:]
        
        # Reverse Stage 2: Remove phase distortion
        np.random.seed(key + 12345)
        phase_indices = np.random.randint(0, self.N, self.N)
        phase_values = np.exp(2j * np.pi * phase_indices / self.N)
        de_phased = symbol_no_cp / phase_values
        
        # Reverse Stage 1: Inverse permutation
        np.random.seed(key)
        permutation = np.random.permutation(self.N)
        inverse_perm = np.argsort(permutation)
        decrypted = de_phased[inverse_perm]
        
        # Re-add CP
        decrypted_with_cp = np.concatenate([
            decrypted[-self.cp_len:],
            decrypted
        ])
        
        return decrypted_with_cp
    
    def awgn_channel(self, signal: np.ndarray, snr_db: float) -> np.ndarray:
        """Simulate AWGN channel."""
        signal_power = np.mean(np.abs(signal) ** 2)
        snr_linear = 10 ** (snr_db / 10)
        noise_power = signal_power / snr_linear
        
        noise = np.sqrt(noise_power / 2) * (
            np.random.randn(len(signal)) +
            1j * np.random.randn(len(signal))
        )
        
        return signal + noise
    
    def demodulate_ofdm(self, received_symbol: np.ndarray) -> np.ndarray:
        """Demodulate OFDM symbol."""
        symbol_no_cp = received_symbol[self.cp_len:]
        freq_domain = np.fft.fft(symbol_no_cp, self.N)
        return freq_domain


def simulate_ber(
    snr_range_db: np.ndarray,
    N: int = 64,
    num_symbols: int = 500,
    key: int = 42
) -> Tuple[List[float], List[float], List[float]]:
    """
    Simulate BER for three scenarios:
    1. Legacy OFDM → Bob
    2. Encrypted-OFDM → Bob (correct key)
    3. Encrypted-OFDM → Eve (no key)
    """
    system = EncryptedOFDM(N=N)
    
    ber_legacy_bob = []
    ber_encrypted_bob = []
    ber_encrypted_eve = []
    
    print("\n" + "=" * 70)
    print("SIMULATION STARTED")
    print(f"Parameters: N={N}, Symbols/SNR={num_symbols}, Key={key}")
    print("=" * 70)
    print(f"{'SNR (dB)':<10} {'Legacy BER':<15} {'Bob BER':<15} {'Eve BER':<15}")
    print("-" * 70)
    
    for snr_db in snr_range_db:
        errors_legacy = 0
        errors_bob = 0
        errors_eve = 0
        total_bits = 0
        
        for _ in range(num_symbols):
            bits = system.generate_bits(N)
            total_bits += N
            symbols = system.bpsk_modulate(bits)
            
            # SCENARIO 1: LEGACY OFDM
            tx_legacy = system.generate_ofdm_symbol(symbols)
            rx_legacy = system.awgn_channel(tx_legacy, snr_db)
            demod_legacy = system.demodulate_ofdm(rx_legacy)
            detected_legacy = system.bpsk_demodulate(demod_legacy[:N])
            errors_legacy += np.sum(detected_legacy != bits)
            
            # SCENARIO 2: ENCRYPTED-OFDM → BOB
            tx_encrypted = system.encrypt_symbol(tx_legacy, key)
            rx_encrypted = system.awgn_channel(tx_encrypted, snr_db)
            rx_decrypted = system.decrypt_symbol(rx_encrypted, key)
            demod_bob = system.demodulate_ofdm(rx_decrypted)
            detected_bob = system.bpsk_demodulate(demod_bob[:N])
            errors_bob += np.sum(detected_bob != bits)
            
            # SCENARIO 3: ENCRYPTED-OFDM → EVE
            demod_eve = system.demodulate_ofdm(rx_encrypted)
            detected_eve = system.bpsk_demodulate(demod_eve[:N])
            errors_eve += np.sum(detected_eve != bits)
        
        ber_legacy_bob.append(errors_legacy / total_bits)
        ber_encrypted_bob.append(errors_bob / total_bits)
        ber_encrypted_eve.append(errors_eve / total_bits)
        
        print(f"{snr_db:<10.0f} {ber_legacy_bob[-1]:<15.6f} "
              f"{ber_encrypted_bob[-1]:<15.6f} {ber_encrypted_eve[-1]:<15.6f}")
    
    print("=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    
    return ber_legacy_bob, ber_encrypted_bob, ber_encrypted_eve


def plot_results(
    snr_range: np.ndarray,
    ber_legacy: List[float],
    ber_bob: List[float],
    ber_eve: List[float]
) -> None:
    """Generate BER comparison plot."""
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    ax.semilogy(snr_range, ber_legacy, 'b-o',
                linewidth=2.5, markersize=8, markerfacecolor='white',
                markeredgewidth=2, label='Legacy OFDM (Bob)')
    
    ax.semilogy(snr_range, ber_bob, 'g-s',
                linewidth=2.5, markersize=8, markerfacecolor='white',
                markeredgewidth=2, label='Encrypted-OFDM (Bob - correct key)')
    
    ax.semilogy(snr_range, ber_eve, 'r--^',
                linewidth=2.5, markersize=8, markerfacecolor='white',
                markeredgewidth=2, label='Encrypted-OFDM (Eve - no key)')
    
    ax.axhline(y=0.5, color='gray', linestyle=':',
               linewidth=2, alpha=0.7, label='Random Guessing (BER=0.5)')
    
    ax.set_xlabel('SNR (dB)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Bit Error Rate (BER)', fontsize=14, fontweight='bold')
    ax.set_title('Encrypted-OFDM: Physical Layer Security Analysis\n'
                 'Inspired by Mohammed & Saha, Elsevier Computer Networks 2024',
                 fontsize=13, fontweight='bold')
    
    ax.legend(loc='lower left', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, which='both', linestyle='--')
    ax.set_xlim([snr_range[0], snr_range[-1]])
    ax.set_ylim([1e-4, 1])
    
    ax.annotate('Eve cannot decode\n(BER ≈ 0.5)',
                xy=(20, 0.48), xytext=(12, 0.15),
                fontsize=10, color='red',
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
    
    ax.annotate('Bob decodes normally\n(same as Legacy)',
                xy=(15, ber_bob[10] if len(ber_bob) > 10 else ber_bob[-1]), 
                xytext=(5, 0.001),
                fontsize=10, color='green',
                arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
    
    plt.tight_layout()
    
    plt.savefig('results/ber_comparison.png', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print("\n[SAVED] results/ber_comparison.png")
    
    plt.show()


def main():
    """Main entry point."""
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║              ENCRYPTED-OFDM SIMULATION                            ║
║     Based on: Mohammed & Saha (Elsevier 2024)                    ║
║     Implementation by: Niloy Saha                                 ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Parameters
    snr_range = np.arange(-5, 26, 2)
    N = 64
    num_symbols = 500
    key = 42
    
    # Run simulation
    ber_legacy, ber_bob, ber_eve = simulate_ber(
        snr_range, N, num_symbols, key
    )
    
    # Generate plot
    plot_results(snr_range, ber_legacy, ber_bob, ber_eve)
    
    # Summary
    print("\n" + "=" * 70)
    print("KEY FINDINGS:")
    print("=" * 70)
    print("1. Legacy OFDM and Encrypted-OFDM (Bob) have similar BER")
    print("2. Eve's BER stays at ~0.5 (random guessing)")
    print("3. Physical layer security achieved without upper-layer overhead")
    print("=" * 70)


if __name__ == '__main__':
    main()
