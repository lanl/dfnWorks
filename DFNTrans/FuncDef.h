
#define  pi 3.14159265359
/*! The directory/path for particle tracking outputs, defined by user */
extern char maindir[125];

/*! Fracture porosity, used in velocity reconstructions, defined by user */
extern double porosity;

/*! Flow density, defined by user */
extern double density;

/*! Max number of time steps used for each particles movements, defined by user */
extern unsigned long int timesteps;

/*! One value for all fractures aperture (defined by user), used in case when fracture aperture is not provided by user */
extern double thickness;

/*! Flow saturation, defined by user */
extern double saturation;

/*! Time unit multiplier, converts calculated time/velocities according to required time units */
extern double timeunit;

/*! Name of Control file with all inut parameters to dfnTrans, given by user at the command line*/
extern char controlfile[120];

/*! Total Flow flux on in-flow boundary, calculated in the code */
extern double totalFluxIn;

/* parts_fracture: initial number of particles per fracture */
/* Global variables: nnodes - number of nodes     */
/* ncells - number of triangles */
/* nfract - number of fractures */
/* max_neighb - maximum number of edges in Voronoi polygon, node connections */

/*! pflotran=1 when PFLOTRAN flow solver is used */
extern unsigned int pflotran;

/*! fehm=1 when FEHM flow solver is used */
extern unsigned int fehm;

/*! total number of nodes in the DFN mesh */
extern unsigned int nnodes;

/*! total number of triangular elements in the DFN mesh */
extern unsigned int ncells;

/*! total number of fractures in the DFN mesh */
extern unsigned int nfract;

/*! maximum number of nodes neighbours/connections*/
extern unsigned int max_neighb;

/*! initial number of particles set up in the simulation */
extern unsigned int npart;

/*! index of current particle, idex in particle's loop */
extern unsigned int np;

/*! number of nodes in in-flow boundary face/zone */
extern unsigned int nzone_in;

/*! pointer to the dynamic array with a list of in-flow boundary nodes */
extern unsigned int *nodezonein;

/*! pointer to the dynamic array with a list of out-flow boundary nodes */
extern unsigned int *nodezoneout;

extern unsigned int flag_w;



/*! Material structure contains fracture parameters, read from DFN mesh */
struct material {
    
    /*! angle that fracture makes with z axis*/
    float theta;
    
    /*! rotation vector for rotating fracture to xy plane */
    float nvect_xy[2];
    
    /*! rotation vector for rotating fracture back to xyz domain */
    float nvect_z[2];
    
    /*! index of first node in a fracture (doesn't include the intersection nodes) */
    unsigned int firstnode;
    
    /*! index of last node in a fracture (doesn't include the intersection nodes) */
    unsigned int lastnode;
    
    /*! index of first triangular cell in a fracture */
    unsigned int firstcell;
    
    /*! total number of triangular cells in a fracture */
    unsigned int numbcells;
    
    /*! rotational matrix from 3d to 2d */
    double rot2mat[3][3];
    
    /*! rotational matrix from 2d to 3d */
    double rot3mat[3][3];
};


/*! Vertex is a node structure and contains all the information about the node/vertex of the DFN mesh */
struct vertex {
    
    /*! node type: 0 - interior node; 10 - boundary (exterior) node; 2 - intersection (interface) node; 12 - intersection boundary node; 300, 310, 302, 312 - node in in-flow boundary; 200, 210, 202, 212 - node in out-flow boundary */
    unsigned int typeN;
    
    /*! fracture ID where node is */
    unsigned int fracture[2];
    
    /*! node's x,y,z coordinations */
    double coord[3];
    
    /*! XYZ plane coordination of node; if the node is on intersection then two sets of XYZ coordinations are defined (each set for each intersecting fracture */
    double coord_xy[6];
    
    /*! Voronoi polygon vlue associated with the cell center */
    double pvolume;  // volume of Voronoi polygon
    
    /*! fluid pressure defined at the node by flow solver */
    double pressure; //pressure
    
    /*!  number of nodes connections */
    unsigned int numneighb;  //number of neighboring nodes
    
    /*! reconstructed Darcy velocity at the node, four velocities are defined at intersection nodes */
    double velocity[4][2]; //Darcy's velocity
    
    /*! appropriate time step for particles is defined at the node according to the volume of control volume cell */
    double timestep[4]; // time step
    
    /*! dynamic array of neighboring nodes ID*/
    unsigned int* indnodes; //array of neighboring node's indices
    
    /*! dynamic array of triangular cells ID */
    unsigned int** cells; //array of neighboring cells's indices
    
    /*! dynamic array of fractures ID */
    unsigned int** fracts;//array of fracture's numbers
    
    /*! dynamic array of types of neighbouring nodes */
    unsigned int* type; //array of node's type
    
    /*! dynamic array of flow fluxes at the edges of the control volume cell */
    double* flux;//array of fluxes
    
    /*! dynamic array of 2D areas of the edges of the control volume cell */
    double* area;//area of Voronoi facea
    
    /*! residential time of particles inside the control volume cell */
    double residtime; //residential time of particles
    
    /*! fracture aperture at the control volume cell */
    double aperture; //aperture of the cell
};


/* element structure contains the information about trianglar cells in DFN mesh */
struct element {
    /*! fracture ID where cell is located */
    unsigned int fracture;
    
    /*! vertices ID (node indices) */
    unsigned int node_ind[3];// three nodes indices
    
    /*! index of reconstructed velocities at each vertex (index in vertex structure)*/
    unsigned int veloc_ind[3]; // index of velocity of each node
    
    
};


/*! contam structure contains all parameters of the particles */
struct contam{
    
    /*! velocity of particle, interpolated from triangular cell */
    double velocity[2];
    
    /*! x and y particle position on fracture */
    double position[2];
    
    /*! x and y particle position in previous time step */
    double prev_pos[2];
    
    /*! the fracture ID where particle is located  at current time step */
    unsigned int fracture;
    
    /*! the cell ID where particle is located at current time step */
    unsigned int cell;
    
    /*! intcell=1 if cell is on intersection; =0 if not */
    unsigned int intcell;
    
    /*! weights, that are calculated for velocity interpolation from cell vertices */
    double weight[3];
    
    /*! accumulated advective time of particles movement */
    double time;
    
    /*! weight of particle according to flow fluxes in in-flow boundary or according to initial fracture/cell aperture */
    double fl_weight;
    
    /*! interpolated fluid pressure at particles location*/
    double pressure; //fluid pressure
    
    /*! in case of TDRW: total travel time = advection plus diffusion */
    double t_adv_diff; //in case of TDRW - total travel time
    
    /*! in case of TDRW: accumulative  diffusion time */
    double t_diff; // in case of TDRW - accumulative diffusion time
};

/*! DYNAMIC ARRAY OF FRACTURES */
extern    struct material *fracture;

/*! DYNAMIC ARRAY OF NODES in DFN mesh */
extern    struct vertex *node;

/*! DYNAMIC ARRAY OF PARTICLES */
extern    struct contam *particle;

/*! DYNAMIC ARRAY OF TRIANGULAR CELLS in DFN mesh */
extern    struct element *cell;


void ReadInit();
void ReadDataFiles();
void AdjacentCells(int  ln, int i, int  j, int  k);
void Convertto2d();
void Convertto3d();
void DarcyVelocity();
struct matr   MatrixProducts (double normxarea[][2],  int number);
struct lb  DefineBoundaryAngle(int i, unsigned int edge_1, unsigned int edge_2, int f1, int coorf);
void VelocityInteriorNode (double normxarea[][2], int i, int number, unsigned int indj[max_neighb], int vi);
void VelocityExteriorNode (double normxarea[][2], int i, int number, unsigned int indj[max_neighb],struct lb lbound, int vi) ;
void CheckNewCell();
void ParticleTrack();
struct intcoef  CalculateWeights(int nn1, int nn2, int nn3);
void SearchNeighborCells(int nn1, int nn2, int nn3);
int InsideCell (unsigned int numc);
void NeighborCells (int k);
void PredictorStep();
void CorrectorStep();
void DefineTimeStep();
int CheckDistance();
void AcrossIntersection (int prevcell, int int1, int int2, int mixing_rule);
void ChangeFracture(int cell_win);
struct posit3d CalculatePosition3D();
int InitCell ();
int InitPos();
void Moving2Center(int nnp, int cellnumber);
int Moving2NextCell(int stuck, int k);
void BoundaryCells();
int InitParticles_np (int k_current, int firstn, int lastn, int parts_fracture, int first_ind, int last_ind);
int InitParticles_eq (int k_current, int firstn, int lastn, double parts_dist, int first_ind, int last_ind);
int CornerVelocity(int i,int m1,int m2,int m3,int s1,int s2,int s3);
void ReadBoundaryNodes();
FILE *OpenFile(char filen[120], char fileopt[2]);
void ReadFEHMfile(int nedges);
void ReadPFLOTRANfile(int nedges);
void WritingInit();
void Velocity3D();
double CalculateCurrentDT();
int Yindex(int nodenum, int np);
int Xindex(int nodenum, int np);
int CompleteMixingRandomSampling(double products[4], double speedsq[4], int indj, int int1, int indk);
int StreamlineRandomSampling(double products[4], double speedsq[4], int indj, int int1, int indk, int neighborcellind[4], int neighborfracind[4], int prevfrac, int prevcell);
void OutputVelocities();
int XindexC(int nodenum, int ii);
int YindexC(int nodenum, int ii);
double DefineAngle(double u1,double u2, double v1, double v2);
void HalfPolygonVelocity(int i,int k, int fractn, int indc,unsigned int fractj[max_neighb]);
struct posit3d CalculateVelocity3D();
void BoundaryLine(int n1, int n2, int n3);
void CheckGrid();
int BVelocityDirection(int b1, int b2);
double InOutFlowCell(int indcell, int int1, double nposx, double nposy);
void Moving2NextCellBound(int prevcell);
struct inpfile Control_File(char fileobject[], int ctr);
struct inpfile Control_Data(char fileobject[], int ctr);
void ParticleOutput (int currentt, int frac_p);
struct inpfile Control_Param(char fileobject[], int ctr);
void FlowInWeight(int numbpart);
int InitParticles_ones (int k_current, double inter_p[][4], int fracture, int parts_fracture, int ii, double thirdcoor, int zonenumb_in, int first_ind, int last_ind);
void Coordinations2D ();
void ReadAperture();
void InitInMatrix();
double TimeFromMatrix(double pdist);
void FinalPosition();
struct lagrangian CalculateLagrangian(double xcurrent, double ycurrent, double zcurrent, double xprev, double yprev, double zprev);
void OutputMarPlumDisp (int currentnum, char path[125]);
int String_Compare(char string1[], char string2[]);
struct inpfile Control_File_Optional(char fileobject[], int ctr);
double TimeDomainRW (double time_advect);
int InitParticles_flux (int k_current, int firstn, int lastn, double weight_p);

