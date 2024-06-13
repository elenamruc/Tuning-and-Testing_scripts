import ROOT

def process_directory(directory, histogram_name):
    """
    Recursively searches a ROOT directory and its subdirectories for a histogram with a specific name.
    """
    for key in directory.GetListOfKeys():
        obj = key.ReadObj()
        if obj.IsA().InheritsFrom(ROOT.TDirectory.Class()):
            # Recursive search in subdirectories
            result = process_directory(obj, histogram_name)
            if result:
                return result
        elif obj.IsA().InheritsFrom(ROOT.TCanvas.Class()):
            # Return the histogram if the name matches
            if obj.GetName() == histogram_name:
                for prim in obj.GetListOfPrimitives():
                    if prim.InheritsFrom(ROOT.TH1.Class()):
                        # Clone and rename the histogram to manipulate freely
                        cloned_hist = prim.Clone("Digital Module")
                        return cloned_hist
    return None

def superimpose_histograms_from_files(root_file1, root_file2, root_file3, histogram_name, new_axis_title, save_name, range_x_min, range_x_max, xe_pos, ye_pos, add_axis=False):
    """
    Opens multiple ROOT files and superimposes specified histograms on a single canvas.
    """
    # Try to open the ROOT files
    files = [ROOT.TFile.Open(root_file, "READ") for root_file in [root_file1, root_file2, root_file3]]
    if not all(f.IsOpen() for f in files):
        print("No se pudieron abrir los archivos correctamente.")
        return

    # Gets the histograms
    histograms = [process_directory(f, histogram_name) for f in files]
    
    # Overlay histograms on a new TCanvas
    superimpose_canvas = ROOT.TCanvas("superimpose", "Histogramas Superpuestos", 1150, 800)
    
    # Sets the histogram title
    histograms[0].SetTitle(f"{new_axis_title} distribution")
    
    # Draw the histograms on the TCanvas
    histograms[0].Draw()
    histograms[1].Draw("SAME")
    histograms[2].Draw("SAME")
    
    # Set margins
    superimpose_canvas.SetLeftMargin(0.12)
    superimpose_canvas.SetRightMargin(0.1)

    # Set axis titles and labels for each histogram
    histograms[0].SetTitle("")
    histograms[1].SetTitle("")
    histograms[2].SetTitle("")
    
    histograms[0].GetXaxis().SetRangeUser(range_x_min, range_x_max)
    histograms[1].GetXaxis().SetRangeUser(range_x_min, range_x_max)
    histograms[2].GetXaxis().SetRangeUser(range_x_min, range_x_max)  
    
    histograms[0].SetLineColor(ROOT.kRed)
    histograms[1].SetLineColor(ROOT.kBlue)
    histograms[2].SetLineColor(ROOT.kBlack)
    histograms[0].SetLineWidth(2)
    histograms[1].SetLineWidth(2)
    histograms[2].SetLineWidth(2)
    
    
    # Set range and style for histogram of digital module
    histograms[0].GetXaxis().SetTitleSize(34)
    histograms[0].GetXaxis().SetTitleFont(43)
    histograms[0].GetYaxis().SetTitleSize(34)
    histograms[0].GetYaxis().SetTitleFont(43)
    histograms[0].GetZaxis().SetTitleSize(34)  
    histograms[0].GetZaxis().SetTitleFont(43)  
    histograms[0].GetZaxis().SetTitleOffset(1.8)
    histograms[0].GetXaxis().SetLabelSize(0.04)  
    histograms[0].GetYaxis().SetLabelSize(0.04)      
    
    # Set range and style for histogram of w7-24
    histograms[1].GetXaxis().SetTitleSize(34)
    histograms[1].GetXaxis().SetTitleFont(43)
    histograms[1].GetYaxis().SetTitleSize(34)
    histograms[1].GetYaxis().SetTitleFont(43)
    histograms[1].GetZaxis().SetTitleSize(34)  
    histograms[1].GetZaxis().SetTitleFont(43)  
    histograms[1].GetZaxis().SetTitleOffset(1.8)
    histograms[1].GetXaxis().SetLabelSize(0.04)  
    histograms[1].GetYaxis().SetLabelSize(0.04)   
    
    # Set range and style for histogram of w7-31
    histograms[2].GetXaxis().SetTitleSize(34)
    histograms[2].GetXaxis().SetTitleFont(43)
    histograms[2].GetYaxis().SetTitleSize(34)
    histograms[2].GetYaxis().SetTitleFont(43)
    histograms[2].GetZaxis().SetTitleSize(34)
    histograms[2].GetZaxis().SetTitleFont(43)  
    histograms[2].GetZaxis().SetTitleOffset(1.8)
    histograms[2].GetXaxis().SetLabelSize(0.04) 
    histograms[2].GetYaxis().SetLabelSize(0.04)    
    
    
    
    
    # Statistics box for digital module
    stats_box_1 = histograms[0].GetListOfFunctions().FindObject("stats")
    stats_box_1.SetX1NDC(0.68)
    stats_box_1.SetY1NDC(0.72)  
    stats_box_1.SetX2NDC(0.89)
    stats_box_1.SetY2NDC(0.62)
    stats_box_1.Draw()
    stats_box_1.Draw()

    # Statistics box for w7-24
    stats_box_2 = histograms[1].GetListOfFunctions().FindObject("stats")
    stats_box_lines_2 = stats_box_2.GetListOfLines()
    stats_box_lines_2[0].SetTitle("w7-24") # Set title 
    stats_box_2.SetX1NDC(0.68)
    stats_box_2.SetY1NDC(0.61)
    stats_box_2.SetX2NDC(0.89)
    stats_box_2.SetY2NDC(0.51)
    stats_box_2.Draw()
    
    
    # Statistics box for w7-31
    stats_box_3 = histograms[2].GetListOfFunctions().FindObject("stats")
    stats_box_lines_3 = stats_box_3.GetListOfLines()
    stats_box_lines_3[0].SetTitle("w7-31") # Set title
    stats_box_3.SetX1NDC(0.68)
    stats_box_3.SetY1NDC(0.50)
    stats_box_3.SetX2NDC(0.89)
    stats_box_3.SetY2NDC(0.40)
    stats_box_3.Draw()
    

    # Update the statistics box to display relevant information
    def update_stats_box(histogram, new_title):
        stats_box = histogram.GetListOfFunctions().FindObject("stats")
        if not stats_box:
            return 

        stats_box_lines = stats_box.GetListOfLines()
        for item in stats_box_lines:
            #if isinstance(item, ROOT.TLatex) and "Entries" not in item.GetTitle():
            if "Entries" not in item.GetTitle():
                # Change title
                item.SetTitle(new_title)
                break

        superimpose_canvas.Modified()
        superimpose_canvas.Update()


    # Add a legend to the canvas after drawing the histograms
    legend = ROOT.TLegend(0.68, 0.73, 0.89, 0.83)
    legend.AddEntry(histograms[0], "Digital module")
    legend.AddEntry(histograms[1], "Hybrid module w7-24")
    legend.AddEntry(histograms[2], "Hybrid module w7-31")
    legend.Draw()

    if add_axis:
        superimpose_canvas.Update()  # Canvas update


        y_pos = ROOT.gPad.GetUymax()
							
    superimpose_canvas.Update()
    superimpose_canvas.SaveAs(save_name)

    # Close files
    for f in files:
        f.Close()

def get_histogram_range(root_file, histogram_name):
    """
    Fetches the minimum and maximum ranges of the X-axis of a given histogram.
    """
    file = ROOT.TFile.Open(root_file, "READ")
    if not file or not file.IsOpen():
        print(f"Failed to open file {root_file}")
        return None, None

    hist = process_directory(file, histogram_name)
    if not hist:
        print(f"Histogram {histogram_name} not found in {root_file}")
        return None, None

    x_min = hist.GetXaxis().GetXmin()
    x_max = hist.GetXaxis().GetXmax()
    file.Close()
    return x_min, x_max
    

def main():
    """
    Main function to execute the superimposition of histograms and fetch range data.
    """
    # Root files path and histogram name
    root_file1 = "../tuning_chip_20240301/Results/Run000022_SCurve.root"
    root_file2 = "../tuning_sensor_w7-24/Results/Run000017_SCurve.root"
    root_file3 = "../tuning_sensor_w7-31/Results/Run000019_SCurve.root"
    histogram_name_1 = "D_B(0)_O(0)_H(0)_Noise1D_Chip(15)"

    x1n, x2n = get_histogram_range(root_file1, histogram_name_1)
    superimpose_histograms_from_files(root_file1, root_file2, root_file3, histogram_name_1, "Noise", "Noise1D_All_Targets.png", 0, 60, 0, 287.86, add_axis=True)


if __name__ == "__main__":
    main()
