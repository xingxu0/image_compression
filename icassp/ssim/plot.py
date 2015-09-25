label_size = 20

def set_plt(plt):
	plt.tick_params(axis='both', which='major', labelsize=label_size)
	plt.tick_params(axis='both', which='minor', labelsize=label_size)
	plt.tight_layout()

def set_ax(ax):
	ax.tick_params(axis='both', which='major', labelsize=label_size)
	ax.tick_params(axis='both', which='minor', labelsize=label_size)


label_font_size = 26 
legend_font_size = 21
line_width = 3
