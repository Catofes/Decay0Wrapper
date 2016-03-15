#include <iostream>
#include <fstream>
#include <TH1D.h>
#include <TMath.h>

using std::ifstream;
using std::cout;
using std::cerr;
using std::endl;
void DataLoader(const char * filename)
{
    ifstream fin(filename);
    if (!fin.is_open()) {
        cerr << "can't find the file " << filename << endl;
        return;
    }
    int evt_num, n_particles;
    int partile_num, pdg_code;
    double px, py, pz;
    TH1D * th1 = new TH1D("th1", "The total energy", 300, 0, 3.0);
    for (;fin >> evt_num >> n_particles;) {
        double total_e = 0;
        for (int i=0; i<n_particles; ++i) {
            fin >> partile_num >> pdg_code >> px >> py >> pz;
            total_e += TMath::Sqrt((px*px+py*py+pz*pz)*1000*1000 + 0.510998910*0.510998910);
            total_e -= 0.510998910;
        }
        cout << total_e << endl;
        th1->Fill(total_e);
    }
    fin.close();
    th1->Draw();
}
