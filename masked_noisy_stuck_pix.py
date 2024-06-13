import ROOT

def read_masked_positions(filename):
    """
    Reads a file and extracts positions where pixels are masked. These positions
    are expected to be listed under lines starting with 'ENABLE', with each
    pixel's status ('0' for masked) listed in comma-separated values.
    """
    with open(filename) as f:
        lines = f.readlines()
    
    masked_positions = set()
    i = 0  # Row counter
    for line in lines:
        if line.startswith("ENABLE"):
            enable_values = line.split()[1].split(",")
            for j, value in enumerate(enable_values):
                if value == "0":  # Check if the pixel is masked
                    masked_positions.add((i, j))
            i += 1
    return masked_positions

def compare_masked_positions(filemasked1, filemasked2):
    """
    Compares the masked positions between two different files and returns the positions
    that are unique to the second file.
    """
    masked_positions1 = read_masked_positions(filemasked1)
    masked_positions2 = read_masked_positions(filemasked2)
    return masked_positions2 - masked_positions1  # Set difference

def create_histogram(masked_positions, title, filename):
    """
    Creates and saves a ROOT histogram of masked positions.
    """
    # Initialize histogram with dimensions for a typical CMOS sensor
    hist = ROOT.TH2F(f"w7-24: {title}", "", 432, 0, 432, 336, 0, 336)
    for pos in masked_positions:
        hist.Fill(*pos)  # Fill histogram at positions

    hist.SetStats(1)  # Enable statistics box to display histogram info
    c = ROOT.TCanvas("c", title, 1150, 800)
    c.SetLeftMargin(0.12)
    c.SetRightMargin(0.1)
    c.SetBottomMargin(0.1)
    hist.Draw()  # Draw the histogram
    
    # Set the axis labels
    hist.GetXaxis().SetTitle("Column")
    hist.GetYaxis().SetTitle("Row")
  
    hist.GetXaxis().SetTitleSize(34)
    hist.GetXaxis().SetTitleFont(43)
    hist.GetYaxis().SetTitleSize(34)
    hist.GetYaxis().SetTitleFont(43)
    hist.GetXaxis().SetLabelSize(0.04) 
    hist.GetYaxis().SetLabelSize(0.04)  
    
    ROOT.gStyle.SetPalette(1)  # Set color palette for the histogram
    c.SaveAs(f"{filename}.png")  # Save the canvas as a PNG image
    
    hist.Write()  # Write the histogram to the ROOT file

def main():
    """
    Main function to process masked pixel data and generate histograms.
    """
    root_file = ROOT.TFile("masked_noisy_stuck.root", "RECREATE")  # Open a single ROOT file for all histograms
    # File paths
    f_masked = "CMSIT_RD53B.txt"
    noise_scan = "Results/Run000014_CMSIT_RD53B.txt"
    pixel_alive = "Results/Run000016_CMSIT_RD53B.txt"

    # Obtain masked, noisy, and stuck positions
    masked_positions = read_masked_positions(f_masked)
    noisy_positions = read_masked_positions(noise_scan)
    stuck_positions = compare_masked_positions(noise_scan, pixel_alive)  # Stuck as defined by appearance in two datasets

    # Generate and save histograms
    create_histogram(masked_positions, "Masked Pixels", "masked_pixels")
    create_histogram(noisy_positions, "Noisy Pixels", "noisy_pixels")
    create_histogram(stuck_positions, "Stuck Pixels", "stuck_pixels")
    
    root_file.Close()  # Close the ROOT file
if __name__ == "__main__":
    main()



    

