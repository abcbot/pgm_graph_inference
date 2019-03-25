"""
Defines GGNN model based on the PGM by GNN workshop paper.
Authors: kkorovin@cs.cmu.edu, markcheu@andrew.cmu.edu
"""

import torch
import torch.nn as nn

class GGNN(nn.Module):
    def __init__(self, n_nodes, state_dim, message_dim, n_steps=10):
        super(GGNN, self).__init__()

        self.state_dim = state_dim
        self.n_nodes = n_nodes
        self.n_steps = n_steps
        self.message_dim = message_dim
        self.propagator = nn.GRU(self.state_dim+self.message_dim, self.state_dim)
        self.message_passing = nn.Sequential(
            nn.Linear(2*self.state_dim+1+2, self.message_dim),
            nn.ReLU(),
            nn.Linear(self.message_dim, self.message_dim),
            nn.ReLU(),
            nn.Linear(self.message_dim, self.message_dim),
            nn.ReLU(),
        )
        self.readout = nn.Sequential(
            nn.Linear(self.state_dim, self.message_dim),
            nn.ReLU(),
            nn.Linear(self.message_dim, self.message_dim),
            nn.ReLU(),
            nn.Linear(self.message_dim, 2),
            nn.ReLU(),
        )
        self.softmax = nn.Softmax(dim=0)
        self.sigmoid = nn.Sigmoid()
        self._initialization()


    def _initialization(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                m.weight.data.normal_(0.0, 0.02)
                m.bias.data.fill_(0)


    #unbatch version for debugging
    def forward(self, J,b):
        readout = torch.zeros(self.n_nodes)
        hidden_states = torch.zeros(self.n_nodes,self.state_dim)
        message_i_j = torch.zeros(self.n_nodes, self.n_nodes, self.message_dim)

        for step in range(self.n_steps):
            for i in range(self.n_nodes):
                for j in range(self.n_nodes):
                    message_in = torch.cat([hidden_states[i,:],hidden_states[j,:],J[i,j].unsqueeze(0),b[i].unsqueeze(0),b[j].unsqueeze(0)])
                    message_i_j[i,j,:] = self.message_passing(message_in)

            message_i=torch.sum(message_i_j,0)

            for i in range(self.n_nodes):
                gru_in = torch.cat([hidden_states[i,:],message_i[i]])
                gru_in = gru_in.unsqueeze(0).unsqueeze(0) #input of shape (seq_len, batch, input_size)                
                hidden_states[i,:],_ = self.propagator(gru_in)
        readout = self.readout(hidden_states)
        readout = self.sigmoid(readout)
        return readout
