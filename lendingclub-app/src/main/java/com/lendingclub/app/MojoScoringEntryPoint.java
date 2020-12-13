package com.lendingclub.app;

import py4j.GatewayServer;

public class MojoScoringEntryPoint {

    private MojoScoring mojoScoring;
    
    public MojoScoringEntryPoint() {
        mojoScoring = new MojoScoring();
    }
    
    public MojoScoring getScorer() {
        return mojoScoring;
    }
    
    public static void main(String[] args) {
        GatewayServer gatewayServer = new GatewayServer(new MojoScoringEntryPoint());
        gatewayServer.start();
        System.out.println("Gateway Server Started");
    }
}