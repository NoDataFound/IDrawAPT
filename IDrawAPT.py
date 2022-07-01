#!/usr/bin/env python
# -*- coding: utf-8 -*-
# cory@darkintel.io
#.___  ________                           _____ _____________________
#|   | \______ \____________ __  _  __   /  _  \\______   \__    ___/
#|   |  |    |  \_  __ \__  \\ \/ \/ /  /  /_\  \|     ___/ |    |   
#|   |  |    `   \  | \// __ \\     /  /    |    \    |     |    |   
#|___| /_______  /__|  (____  /\/\_/   \____|__  /____|ver0 |____|   
#              \/           \/                 \/                   
#
#https://github.com/jina-ai/dalle-flow
#Docker: docker pull jinaai/dalle-flow:latest
from docarray import Document

print('\n')
apt_file = input('[Actor File to Draw] Enter Filename: ')
print('\n')
#server_url = 'grpc://localhost:51005' #Docker Support
server_url = 'grpc://dalle-flow.jina.ai:51005'

with open (apt_file, "r") as actor:
    for apt in actor:
        da = Document(text=apt.strip()).post(server_url, parameters={'num_images': 2}).matches
        da.plot_image_sprites(output=apt.strip()+'.png', show_progress=True, canvas_size=1024, fig_size=(10,10), show_index=True)

