/**
	This software was developed by the University of Tennessee as part of the
	Distributed Data Analysis of Neutron Scattering Experiments (DANSE)
	project funded by the US National Science Foundation.

	If you use DANSE applications to do scientific research that leads to
	publication, we ask that you acknowledge the use of the software with the
	following sentence:

	"This work benefited from DANSE software developed under NSF award DMR-0520547."

	copyright 2008, University of Tennessee
 */
#ifndef MODEL_CLASS_H
#define MODEL_CLASS_H

#include <vector>
#include "parameters.hh"
extern "C" {
	#include "cylinder.h"
	#include "parallelepiped.h"
	#include "lamellarPS.h"
	#include "lamellar.h"
	#include "fuzzysphere.h"
}

using namespace std;



class PearlNecklaceModel{
public:
	// Model parameters
	Parameter scale;
	Parameter radius;
	Parameter edge_separation;
	Parameter thick_string;
	Parameter num_pearls;
	Parameter sld_pearl;
	Parameter sld_string;
	Parameter sld_solv;
	Parameter background;

	// Constructor
	PearlNecklaceModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class FCCrystalModel{
public:
	// Model parameters
	Parameter scale;
	Parameter dnn;
	Parameter d_factor;
	Parameter radius;
	Parameter sldSph;
	Parameter sldSolv;
	Parameter background;
	Parameter theta;
	Parameter phi;
	Parameter psi;

	// Constructor
	FCCrystalModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};


class BCCrystalModel{
public:
	// Model parameters
	Parameter scale;
	Parameter dnn;
	Parameter d_factor;
	Parameter radius;
	Parameter sldSph;
	Parameter sldSolv;
	Parameter background;
	Parameter theta;
	Parameter phi;
	Parameter psi;

	// Constructor
	BCCrystalModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};


class FuzzySphereModel{
public:
	// Model parameters
	Parameter radius;
	Parameter scale;
	Parameter fuzziness;
	Parameter sldSph;
	Parameter sldSolv;
	Parameter background;

	// Constructor
	FuzzySphereModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class HardsphereStructure{
public:
	// Model parameters
	Parameter effect_radius;
	Parameter volfraction;

	// Constructor
	HardsphereStructure();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class StickyHSStructure{
public:
	// Model parameters
	Parameter effect_radius;
	Parameter volfraction;
	Parameter perturb;
	Parameter stickiness;

	// Constructor
	StickyHSStructure();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class SquareWellStructure{
public:
	// Model parameters
	Parameter effect_radius;
	Parameter volfraction;
	Parameter welldepth;
	Parameter wellwidth;

	// Constructor
	SquareWellStructure();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class HayterMSAStructure{
public:
	// Model parameters
	Parameter effect_radius;
	Parameter charge;
	Parameter volfraction;
	Parameter temperature;
	Parameter saltconc;
	Parameter dielectconst;

	// Constructor
	HayterMSAStructure();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class DiamEllipFunc{
public:
	// Model parameters
	Parameter radius_a;
	Parameter radius_b;

	// Constructor
	DiamEllipFunc();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class DiamCylFunc{
public:
	// Model parameters
	Parameter radius;
	Parameter length;

	// Constructor
	DiamCylFunc();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};


class SLDCalFunc{
public:
	// Model parameters
	Parameter fun_type;
	Parameter npts_inter;
	Parameter shell_num;
	Parameter nu_inter;
	Parameter sld_left;
	Parameter sld_right;

	// Constructor
	SLDCalFunc();

	// Operators to get SLD
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};


class CoreShellModel{
public:
	// Model parameters
	Parameter radius;
	Parameter scale;
	Parameter thickness;
	Parameter core_sld;
	Parameter shell_sld;
	Parameter solvent_sld;
	Parameter background;

	// Constructor
	CoreShellModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class CoreFourShellModel{
public:
	// Model parameters
	Parameter scale;
	Parameter rad_core0;
	Parameter sld_core0;
	Parameter thick_shell1;
	Parameter sld_shell1;
	Parameter thick_shell2;
	Parameter sld_shell2;
	Parameter thick_shell3;
	Parameter sld_shell3;
	Parameter thick_shell4;
	Parameter sld_shell4;
	Parameter sld_solv;
	Parameter background;

	// Constructor
	CoreFourShellModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class CoreShellCylinderModel{
public:
	// Model parameters
	Parameter radius;
	Parameter scale;
	Parameter thickness;
	Parameter length;
	Parameter core_sld;
	Parameter shell_sld;
	Parameter solvent_sld;
	Parameter background;
	Parameter axis_theta;
	Parameter axis_phi;

	// Constructor
	CoreShellCylinderModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class EllipsoidModel{
public:
	// Model parameters
	Parameter radius_a;
	Parameter scale;
	Parameter radius_b;
	Parameter sldEll;
	Parameter sldSolv;
	Parameter background;
	Parameter axis_theta;
	Parameter axis_phi;

	// Constructor
	EllipsoidModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class EllipticalCylinderModel{
public:
	// Model parameters
	Parameter r_minor;
	Parameter scale;
	Parameter r_ratio;
	Parameter length;
	Parameter sldCyl;
	Parameter sldSolv;
	Parameter background;
	Parameter cyl_theta;
	Parameter cyl_phi;
	Parameter cyl_psi;

	// Constructor
	EllipticalCylinderModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};
class TriaxialEllipsoidModel{
public:
	// Model parameters
	Parameter scale;
	Parameter semi_axisA;
	Parameter semi_axisB;
	Parameter semi_axisC;
	Parameter sldEll;
	Parameter sldSolv;
	Parameter background;
	Parameter axis_theta;
	Parameter axis_phi;
	Parameter axis_psi;

	// Constructor
	TriaxialEllipsoidModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class FlexibleCylinderModel{
public:
	// Model parameters
	Parameter scale;
	Parameter length;
	Parameter kuhn_length;
	Parameter radius;
	Parameter sldCyl;
	Parameter sldSolv;
	Parameter background;

	// Constructor
	FlexibleCylinderModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class FlexCylEllipXModel{
public:
	// Model parameters
	Parameter scale;
	Parameter length;
	Parameter kuhn_length;
	Parameter radius;
	Parameter axis_ratio;
	Parameter sldCyl;
	Parameter sldSolv;
	Parameter background;

	// Constructor
	FlexCylEllipXModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class StackedDisksModel{
public:
	// Model parameters
	Parameter scale;
	Parameter core_thick;
	Parameter radius;
	Parameter layer_thick;
	Parameter core_sld;
	Parameter layer_sld;
	Parameter solvent_sld;
	Parameter n_stacking;
	Parameter sigma_d;
	Parameter background;
	Parameter axis_theta;
	Parameter axis_phi;

	// Constructor
	StackedDisksModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class LamellarModel{
public:
	// Model parameters
	Parameter scale;
	Parameter bi_thick;
	Parameter sld_bi;
	Parameter sld_sol;
	Parameter background;

	// Constructor
	LamellarModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);

};

class LamellarFFHGModel{
public:
	// Model parameters
	Parameter scale;
	Parameter t_length;
	Parameter h_thickness;
	Parameter sld_tail;
	Parameter sld_head;
	Parameter sld_solvent;
	Parameter background;

	// Constructor
	LamellarFFHGModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);

};



class LamellarPSModel{
public:
	// Model parameters
	Parameter scale;
	Parameter spacing;
	Parameter delta;
	Parameter sld_bi;
	Parameter sld_sol;
	Parameter n_plates;
	Parameter caille;
	Parameter background;

	// Constructor
	LamellarPSModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class LamellarPSHGModel{
public:
	// Model parameters
	Parameter scale;
	Parameter spacing;
	Parameter deltaT;
	Parameter deltaH;
	Parameter sld_tail;
	Parameter sld_head;
	Parameter sld_solvent;
	Parameter n_plates;
	Parameter caille;
	Parameter background;

	// Constructor
	LamellarPSHGModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};


class LamellarPCrystalModel{
public:
	// Model parameters
	Parameter scale;
	Parameter thickness;
	Parameter Nlayers;
	Parameter spacing;
	Parameter pd_spacing;
	Parameter sld_layer;
	Parameter sld_solvent;
	Parameter background;

	// Constructor
	LamellarPCrystalModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class CoreShellEllipsoidModel{
public:
	// Model parameters
	Parameter scale;
	Parameter equat_core;
	Parameter polar_core;
	Parameter equat_shell;
	Parameter polar_shell;
	Parameter sld_core;
	Parameter sld_shell;
	Parameter sld_solvent;
	Parameter background;
	Parameter axis_theta;
	Parameter axis_phi;

	// Constructor
	CoreShellEllipsoidModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class HollowCylinderModel{
public:
	// Model parameters
	Parameter scale;
	Parameter core_radius;
	Parameter radius;
	Parameter length;
	Parameter sldCyl;
	Parameter sldSolv;
	Parameter background;
	Parameter axis_theta;
	Parameter axis_phi;

	//Constructor
	HollowCylinderModel();

	//Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx , double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class MultiShellModel{
public:
	// Model parameters
	Parameter scale;
	Parameter core_radius;
	Parameter s_thickness;
	Parameter w_thickness;
	Parameter core_sld;
	Parameter shell_sld;
	Parameter n_pairs;
	Parameter background;

	//Constructor
	MultiShellModel();

	//Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx , double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class VesicleModel{
public:
	// Model parameters
	Parameter scale;
	Parameter radius;
	Parameter thickness;
	Parameter core_sld;
	Parameter shell_sld;
	Parameter background;

	//Constructor
	VesicleModel();

	//Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx , double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class BinaryHSModel{
public:
	// Model parameters
	Parameter l_radius;
	Parameter s_radius;
	Parameter vol_frac_ls;
	Parameter vol_frac_ss;
	Parameter ls_sld;
	Parameter ss_sld;
	Parameter solvent_sld;
	Parameter background;

	//Constructor
	BinaryHSModel();

	//Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx , double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class BinaryHSPSF11Model{
public:
	// Model parameters
	Parameter l_radius;
	Parameter s_radius;
	Parameter vol_frac_ls;
	Parameter vol_frac_ss;
	Parameter ls_sld;
	Parameter ss_sld;
	Parameter solvent_sld;
	Parameter background;

	//Constructor
	BinaryHSPSF11Model();

	//Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx , double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class Poly_GaussCoil{
public:
	// Model parameters
	Parameter rg;
	Parameter scale;
	Parameter poly_m;
	Parameter background;

	// Constructor
	Poly_GaussCoil();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

class FractalModel{
public:
	// Model parameters
	Parameter radius;
	Parameter scale;
	Parameter fractal_dim;
	Parameter cor_length;
	Parameter sldBlock;
	Parameter sldSolv;
	Parameter background;

	// Constructor
	FractalModel();

	// Operators to get I(Q)
	double operator()(double q);
	double operator()(double qx, double qy);
	double calculate_ER();
	double evaluate_rphi(double q, double phi);
};

#endif