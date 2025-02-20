# Re-generate the top-down rocket PNG image

import matplotlib.pyplot as plt

# Create a transparent figure
fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
fig.patch.set_alpha(0)  # Make background transparent
ax.set_facecolor((0, 0, 0, 0))  # Transparent axis background

# Draw the main rocket body (circle)
rocket_body = plt.Circle((0, 0), 0.3, color='darkblue', ec='black', lw=2)
ax.add_patch(rocket_body)

# Draw fins as an "X" shape
fin_color = 'darkblue'
fin_width = 0.1
fin_length = 0.6

# Fin positions
fins = [
    [[-fin_width, fin_length], [fin_width, fin_length], [0, 0]],  # Top fin
    [[-fin_width, -fin_length], [fin_width, -fin_length], [0, 0]],  # Bottom fin
    [[-fin_length, fin_width], [-fin_length, -fin_width], [0, 0]],  # Left fin
    [[fin_length, fin_width], [fin_length, -fin_width], [0, 0]]  # Right fin
]

for fin in fins:
    ax.add_patch(plt.Polygon(fin, color=fin_color, ec='black', lw=2))

# Remove axes and save the image
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_xticks([])
ax.set_yticks([])
ax.axis('off')

# Save as a transparent PNG
image_path = "../RocketStand V2/data/images/rocket_top_profile.png"
plt.savefig(image_path, transparent=True, bbox_inches='tight', pad_inches=0)
plt.close()

# Provide the new file path

