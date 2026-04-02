import matplotlib.pyplot as plt

metrics = ["Accuracy","Precision","Recall","F1"]
values = [0.91,0.90,0.92,0.91]

plt.bar(metrics,values)
plt.title("Model Performance")
plt.ylabel("Score")
plt.xlabel("Metrics")
plt.show()