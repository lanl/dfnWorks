
#define  pi 3.14159265359 

extern char maindir[125]; 
extern double porosity;
extern double density;
extern unsigned long int timesteps;
extern double thickness;   
extern double saturation; 
extern double timeunit;
extern char controlfile[120];  

/* parts_fracture: initial number of particles per fracture */
/* Global variables: nnodes - number of nodes     */
/* ncells - number of triangles */     
/* nfract - number of fractures */    
/* max_neighb - maximum number of edges in Voronoi polygon */                           

extern unsigned int pflotran;
extern unsigned int fehm;
extern unsigned int nnodes;
extern unsigned int ncells;
extern unsigned int nfract; 
extern unsigned int max_neighb;
extern unsigned int npart;
extern unsigned int np; //current number of particle in particle structure
extern unsigned int nzone_in;
extern unsigned int *nodezonein; 
extern unsigned int *nodezoneout; 
extern unsigned int flag_w;

struct material {    float theta;  // angle of normal vector of fracture with z axis
  float nvect_xy[2]; // vector for rotating to xy plane;
  float nvect_z[2]; // vector for rotating fracture back to xyz domain 
 
  unsigned int firstnode; // index of first node in fracture (doesn't include the intersection nodes) 
  unsigned int lastnode; //index of lastnode in fracture
  unsigned int firstcell; // index of first cell in fracture
  unsigned int numbcells; //number of cells in fracture  
  double rot2mat[3][3]; // rotational matrix from 3d to 2d  
  double rot3mat[3][3]; // rotational matrix from 2d to 3d     
};


  
struct vertex { 
  unsigned int typeN;    // node type
  unsigned int fracture[2]; //number of fracture/fractures 
  double coord[3]; //node's coordinations: x,y,z
  double coord_xy[6]; // node's coordinations in xy plane
  double pvolume;  // volume of Voronoi polygon
  double pressure; //pressure
  unsigned int numneighb;  //number of neighboring nodes
  double velocity[4][2]; //Darcy's velocity
  double timestep[4]; // time step 	
  unsigned int* indnodes; //array of neighboring node's indices 
  unsigned int** cells; //array of neighboring cells's indices  
  unsigned int** fracts;//array of fracture's numbers
  unsigned int* type; //array of node's type
  double* flux;//array of fluxes 
  double* area;//area of Voronoi facea
  double residtime; //residential time of particles 
  double aperture; //aperture of the cell
};

struct element {      unsigned int fracture; // number of fracture to whom cell belongs
  unsigned int node_ind[3];// three nodes indices
  unsigned int veloc_ind[3]; // index of velocity of each node 
                         
                         
};
struct contam{
  double velocity[2]; //velocity of particle, interpolated from cell
  double position[2]; //x and y particle position;
  double prev_pos[2]; // x and y particle position in previous time step
  unsigned int fracture; //the number of fracture where particle is on current time step
  unsigned int cell; //the number of cell where particle is on current time step
  unsigned int intcell; // flag: =1 if cell is on intersection; =0 if not
  double weight[3]; // weights, that are calculated for velocity interpolation from cell vertexes  
  double time; //calculated time that particle in travel  
  double fl_weight; //weight of particle according to flow fluxes in in-flow boundary /or aperture weight/
};

extern    struct material *fracture;
 
extern    struct vertex *node;  

extern    struct contam *particle; 

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
int InsideCell (int numc);
void NeighborCells (int k);
void PredictorStep();
void CorrectorStep(); 
void DefineTimeStep();
int CheckDistance();
void AcrossIntersection (int prevcell, int int1, int int2 );
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
int RandomSampling(double products[4], double speedsq[4], int indj, int int1, int indk);
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
