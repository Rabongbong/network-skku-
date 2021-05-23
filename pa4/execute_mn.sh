#! /bin/bash

sudo nohup ryu-manager ryu-nat/ryu-nat.py &
sudo python3 prac_4_mn.py
