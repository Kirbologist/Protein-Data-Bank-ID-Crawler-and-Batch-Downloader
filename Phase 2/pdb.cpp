#include "pdb.hpp"
#include <sstream>

namespace pdb {
    char convert_amino_3to1(string amino) {
        if (auto search = amino3to1.find(amino); search != amino3to1.end())
            return amino3to1[amino];
        return '?';
    }

    string convert_amino_1to3(char amino) {
        if (auto search = amino1to3.find(amino); search != amino1to3.end())
            return amino1to3[amino];
        return "???";
    }

    string convert_protein_3to1(vector<string> aminos) {
        stringstream converted_string;
        for (string amino : aminos)
            converted_string << convert_amino_3to1(amino);
        return converted_string.str();
    }

    protein::protein(string id, string name) {
        this->id = id;
        this->name = name;
    }

    void protein::add_chain_structures(string protein_string, vector<string> chains) {
        
    }
}