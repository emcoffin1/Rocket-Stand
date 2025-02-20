import matplotlib.pyplot as plt

# Create a transparent figure
fig, ax = plt.subplots(figsize=(8, 2), dpi=100)
fig.patch.set_alpha(0)  # Make background transparent
ax.set_facecolor((0, 0, 0, 0))  # Transparent axis background

# Define rocket body dimensions
body_length = 6.0
body_height = 1.0

# Draw rocket body (terminating in a point on the left side)
body_shape = [
    [-body_length / 2 - 1.0, 0],  # Leftmost point
    [-body_length / 2, -body_height / 2],  # Left bottom
    [body_length / 2, -body_height / 2],  # Right bottom
    [body_length / 2, body_height / 2],  # Right top
    [-body_length / 2, body_height / 2],  # Left top
]

ax.add_patch(plt.Polygon(body_shape, color='purple', ec='black', lw=2))

# Draw fins (trapezoidal shape)
fin_width = 1.2
fin_height = 0.7

fins = [
    [[body_length / 2, -body_height / 2],
     [body_length / 2 + fin_width, -body_height / 2 - fin_height],
     [body_length / 2 + fin_width, body_height / 2 + fin_height],
     [body_length / 2, body_height / 2]]
]

for fin in fins:
    ax.add_patch(plt.Polygon(fin, color='purple', ec='black', lw=2))

# Draw rocket nose cone (triangle)
nose_cone = [
    [body_length / 2, -body_height / 2],
    [body_length / 2 + 1.5, 0],  # Nose tip
    [body_length / 2, body_height / 2]
]
ax.add_patch(plt.Polygon(nose_cone, color='purple', ec='black', lw=2))

# Remove axes and save the image
ax.set_xlim(-4, 4)
ax.set_ylim(-2, 2)
ax.set_xticks([])
ax.set_yticks([])
ax.axis('off')

# Save as a transparent PNG
image_path = "../RocketStand V2/data/images/rocket_side_profile_pointed.png"
plt.savefig(image_path, transparent=True, bbox_inches='tight', pad_inches=0)
plt.close()
