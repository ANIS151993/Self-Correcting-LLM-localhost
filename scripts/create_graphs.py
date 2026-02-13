

import os
import glob
import tensorflow as tf
import matplotlib.pyplot as plt
from collections import defaultdict

LOG_DIR = "logs/trl"
OUTPUT_DIR = "graphs"
SMOOTHING_WEIGHT = 0.85

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    event_files = glob.glob(os.path.join(LOG_DIR, "events.out.tfevents.*"))
    if not event_files:
        print(f"Error: No TensorBoard event files found in {LOG_DIR}")
        return

    print(f"Found {len(event_files)} event file(s). Processing...")
    
    # Use defaultdict to easily append to lists
    scalar_data = defaultdict(list)

    for event_file in event_files:
        try:
            for summary in tf.compat.v1.train.summary_iterator(event_file):
                for value in summary.summary.value:
                    if value.HasField('simple_value'):
                        tag = value.tag
                        step = summary.step
                        val = value.simple_value
                        scalar_data[tag].append((step, val))
        except Exception as e:
            print(f"Warning: Could not process file {event_file}. Error: {e}")

    if not scalar_data:
        print("No scalar data found in the event files.")
        return

    print(f"Found data for {len(scalar_data)} unique tags. Generating plots...")

    for tag, values in scalar_data.items():
        # Sort values by step
        values.sort(key=lambda x: x[0])
        steps, raw_vals = zip(*values)
        
        # Apply exponential moving average for smoothing
        smoothed_vals = []
        last_val = raw_vals[0]
        for val in raw_vals:
            last_val = SMOOTHING_WEIGHT * last_val + (1 - SMOOTHING_WEIGHT) * val
            smoothed_vals.append(last_val)

        plt.style.use('seaborn-v0_8-darkgrid')
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Plot both raw and smoothed data
        ax.plot(steps, raw_vals, alpha=0.3, label='Raw Data')
        ax.plot(steps, smoothed_vals, color='#C44E52', label=f'Smoothed (α={SMOOTHING_WEIGHT})')

        # Formatting
        clean_tag = tag.replace('/', '_')
        ax.set_title(f"Metric: {tag}", fontsize=16, pad=20)
        ax.set_xlabel("Step", fontsize=12)
        ax.set_ylabel("Value", fontsize=12)
        ax.legend()
        plt.tight_layout()
        
        output_path = os.path.join(OUTPUT_DIR, f"{clean_tag}.png")
        plt.savefig(output_path)
        plt.close(fig)
        print(f"  - Saved plot to {output_path}")

    print("\n✅ All plots generated successfully.")

if __name__ == "__main__":
    # Suppress TensorFlow INFO and WARNING messages
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    main()

