package com.lendingclub.app;

import hex.genmodel.MojoModel;
import hex.genmodel.easy.EasyPredictModelWrapper;
import hex.genmodel.easy.RowData;
import java.io.IOException;
import java.util.*;
import java.lang.*;
import java.net.URL;
import hex.genmodel.*;
import hex.genmodel.easy.exception.PredictException;
import hex.genmodel.easy.prediction.BinomialModelPrediction;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class MojoScoring {
    public MojoModel model = null;
    public EasyPredictModelWrapper predictModel = null;
    
    // Constructor to load MOJO ahead of time and IMPORTANTLY ONLY ONCE
    public MojoScoring() {
        if(this.model == null){
            try{
                URL mojoURL = MojoScoring.class.getClassLoader().getResource("final_gbm.zip");
                
                MojoReaderBackend reader = MojoReaderBackendFactory.createReaderBackend(
                    mojoURL, MojoReaderBackendFactory.CachingStrategy.MEMORY);
                
                this.model = ModelMojoReader.readFrom(reader);
                
                this.predictModel = new EasyPredictModelWrapper(this.model);
                }
            catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    
    // Convert json string into an h2o RowData object
    public RowData createInput(String json){
        JsonObject jsonObject = new JsonParser().parse(json).getAsJsonObject();
        
        RowData rowData = new RowData();
        
        Set<Map.Entry<String, JsonElement>> entrySet = jsonObject.entrySet();
        
        for(Map.Entry<String,JsonElement> entry : entrySet){
          rowData.put(entry.getKey(), jsonObject.get(entry.getKey()).getAsString());
        }
    
        return rowData;
    }

    // Make a model prediction given json String input
    public String predict(String json) throws PredictException {
        try{
            RowData rowData = new RowData();
            rowData = this.createInput(json);
            
            BinomialModelPrediction preds;
            
            preds = this.predictModel.predictBinomial(rowData);
            
            String[] labels;
            
            labels = this.predictModel.getResponseDomainValues();
            
            JsonObject jsonOutput = new JsonObject();

            for (int i = 0; i < preds.classProbabilities.length; i++) {
                jsonOutput.addProperty(labels[i], preds.classProbabilities[i]);
            }

            return jsonOutput.toString();
        }
        catch(PredictException e) {
            e.printStackTrace();
            JsonObject jsonOutput = new JsonObject();
            return jsonOutput.toString();
        }
    }    
}