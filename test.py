# # import asyncio
# # import websockets

# # async def hello():
# #     uri = "ws://165.22.123.190:8005/sample"
# #     async with websockets.connect(uri) as websocket:
# #         while True:
# #             await websocket.send("Hi")

# # asyncio.get_event_loop().run_until_complete(hello())
# import pickle

# import numpy as np
# import matplotlib.pyplot as plt

# # with open('X_test.pkl', 'rb') as f:
# #     x = pickle.load(f)

# # print(x[0].shape)

# with open('data.txt','r') as file:
#     data = file.read().split('\n')[:-2]
#     data = [int(x) for x in data]
#     print(len(data))
#     result = [[]for i in range(8)]
#     for i, x in enumerate(data):
#         if i == 8 * 5000:
#             break
#         result[i % 8].append(x)
#     data = np.transpose(np.array(result))
#     print(data.shape)

# # Create a random 500x8 NumPy array for demonstration
# # data = x[5]

# # Create a figure and a grid of subplots
# fig, axes = plt.subplots(nrows=8, ncols=1, figsize=(8, 16), sharex=True)

# # Iterate through each column and plot it on a separate subplot
# for i in range(8):
#     axes[i].plot(data[:, i])
#     axes[i].set_ylabel(f'Axis {i+1}')

# # Add labels and a title to the overall figure
# fig.suptitle('Plotting 8 Axes')
# axes[-1].set_xlabel('Sample Index')

# # Adjust the layout to prevent overlapping labels
# plt.tight_layout()
# plt.show()



# import pickle
# import numpy as np
# import matplotlib.pyplot as plt



# with open('data.pkl', 'rb') as file:
#     loaded_array = pickle.load(file)


# data = np.transpose(loaded_array)

# fig, ax = plt.subplots(figsize=(10, 6))

# # Plot each stream on the same set of axes
# for i in range(8):
#     ax.plot(data[i], label=f'Stream {i + 1}')

# # Add legend to distinguish between streams
# ax.legend()

# # Add labels if needed
# plt.xlabel('Time')
# plt.ylabel('Value')

# # Show the plot
# plt.show()

# print(loaded_array.shape)


import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto(bytes('test message', "utf-8"), ("165.22.123.190", 8888))
