# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 08:05:09 2020

@author: dgregoriev

This represents a matrix
"""
import math
class Matrix3d():
    '''
    This object represents a matrix of entries
    Permissible inputs are:
    Matrix()
    Matrix3d(direct=list(list()))
    Matrix3d(rows=#,cols=#)
    '''
    def __init__(self,**kwargs):
        self.matrix = []
        
        rows = 0
        cols = 0
        #first check to see if the rows and columns is specified
        for entry in kwargs:
            formatentry = entry.lower()
            if formatentry=='rows':
                rows = kwargs[entry]
            elif formatentry=='cols':
                cols = kwargs[entry]
            elif formatentry=='direct':
                self.matrix = kwargs[entry]
                return #the list defines the matrix
        for r in range(rows):
            newrow = []
            for c in range(cols):
                newrow.append(0)
            self.matrix.append(newrow)
        #now we have dimension if that was needed
        
    def col(self,colindex):
        '''
        This returns a list of the column with the desired index
        '''
        returnlist = []
        for row in self.matrix:
            returnlist.append(row[colindex])
        return returnlist
    
    def row(self, rowindex):
        '''
        This returns a list of the row with the desired index
        '''
        return self.matrix[rowindex]
        
    def numcols(self):
        '''
        This returns the number of columns in the matrix
        '''
        return len(self.matrix[0])
    
    def numrows(self):
        '''
        This returns the number of rows in the matrix
        '''
        return len(self.matrix)
        
    def T(self):
        '''
        This returns a transpose of the matrix (does not change the underlying)
        '''
        newlist = []
        for colindex in range(self.numcols()):
            newlist.append(self.col(colindex))
        return Matrix3d(direct = newlist)
    
    def __add__(self,other):
        '''
        This adds the matrix to another matrix
        '''
        valid = isinstance(other,Matrix3d)
        if valid==False: 
            raise('Matrix must be added to another Matrix')
        #make sure the dimensions are the same
        cols = self.numcols()
        rows = self.numrows()
        if cols!=other.numcols():
            raise('Matrix column size must match')
        if rows!=other.numrows():
            raise('Matrix row size must match')
        newmatrix = []
        for r in range(rows):
            newcol = []
            for c in range(cols):
                newcol.append(self.matrix[r][c]+other.matrix[r][c])
            newmatrix.append(newcol)
        return Matrix3d(direct=newmatrix)
            
    def __sub__(self, other):
        '''
        This subtracts the other matrix from the present matrix
        '''
        valid = isinstance(other,Matrix3d)
        if valid==False: 
            raise('Matrix must be subtracted by another Matrix')
        #make sure the dimensions are the same
        cols = self.numcols()
        rows = self.numrows()
        if cols!=other.numcols():
            raise('Matrix column size must match')
        if rows!=other.numrows():
            raise('Matrix row size must match')
        newmatrix = []
        for r in range(rows):
            newcol = []
            for c in range(cols):
                newcol.append(self.matrix[r][c]-other.matrix[r][c])
            newmatrix.append(newcol)
        return Matrix3d(direct=newmatrix)
    
    def __mul__(self, other):
        '''
        This multiplies the matrices together
        '''
        validMatrix = isinstance(other,Matrix3d)
        validfloat = isinstance(other,float)
        validint = isinstance(other,int)
        if validMatrix==True: 
            #make sure the other's # of rows is the same as the # of cols
            mycols = self.numcols()
            otherrows = other.numrows()
            if mycols!=otherrows:
                raise('Matrix dimensions do not match for multiplication')
            outmatrix = Matrix3d(rows=self.numrows(),cols=other.numcols())
            for r in range(self.numrows()):
                myrow = self.matrix[r]
                for c in range(other.numcols()):
                    othercol = other.col(c)
                    summation = 0
                    for enindex in range(len(myrow)):
                        summation = summation+(myrow[enindex]*othercol[enindex])
                    outmatrix.matrix[r][c] = summation
            return outmatrix
        elif(validfloat==True or validint==True):
            #this multiplies the value across everything
            newlist = []
            for r in range(self.numrows()):
                newcol = []
                for c in range(self.numcols()):
                    newcol.append(self.matrix[r][c]*other)
                newlist.append(newcol)
            return Matrix3d(direct=newlist)
        else:
            raise('Matrix must be multiplied by another Matrix or float/integer')
    
    def minor(self,i,j):
        '''
        This returns the matrix minor for a given row and column 
        '''
        newlist = []
        for r in range(self.numrows()):
            if r==i:
                continue
            newcol = []
            for c in range(self.numcols()):
                if c==j:
                    continue
                newcol.append(self.matrix[r][c])
            newlist.append(newcol)
        submatrix= Matrix3d(direct=newlist)
        return submatrix.det()
        
    def cofac(self,i=None,j=None):
        '''
        This returns the cofactor for a particular entry or the entire matrix
        '''
        if i==None and j==None:
            #this is asking for the full matrix
            newlist = []
            #method omits the top row
            #firstrow =
            for r in range(self.numrows()):
                newcol = []
                for c in range(self.numcols()):
                    newcol.append(self.cofac(r,c))
                newlist.append(newcol)
            return Matrix3d(direct=newlist)
        posneg = (-1)**(i+j)
        return self.minor(i,j)*posneg
    
    def det(self):
        '''
        This returns the determinant of the matrix
        '''
        #check to see if it is a 1d matrix
        if self.numrows()==1:
            return self.matrix[0][0]
        #go through each column
        summation = 0
        for c in range(self.numcols()):
            summation =summation+self.cofac(0,c)*self.matrix[0][c]
        return summation
        
    def adj(self):
        '''
        This returns the adjugate of the matrix
        '''
        return self.cofac().T()
    
    def is_inv(self,zerothreshold=1e-32):
        '''
        This returns true if the matrix is invertible
        or false if the matrix is not invertible
        '''
        matdet = abs(self.det())
        if matdet<=zerothreshold:
            return False
        else:
            return True
            
        
    def inv(self):
        '''
        This is meant to return the inverse of a square matrix
        '''
        if self.is_inv()==False:
            return None
        else:
            invmatdet = 1/self.det()
            return self.adj()*invmatdet        
    
    def __repr__(self):
        outputstr = ''
        for r in range(self.numrows()):
            for c in range(self.numcols()):
                outputstr = outputstr+str(self.matrix[r][c])+', '
            outputstr = outputstr[:-2]
            outputstr = outputstr+'\n'
        return (outputstr)
                        
'''
class Imatrix3d(Matrix3d):
    #This defines an Identity matrix of a specified size
    
    def __init__(self,rows,cols):
        super().__init__(rows=rows,cols=cols)
        for r in range(self.numrows()):
            self.matrix[r][r] = 1
'''

class Matrix4d(Matrix3d):
    '''
    This specifically deals w/ 4 dimensional matrices. The intent is that
    this is used to perform translations, rotations and scaling operations
    on items
    Acceptable constructors are:
        Matrix4d(base=) #this means there is a base entity that this should build from
        Matrix4d(**normal Matrix3d inputs**)...
    '''
    def __init__(self,**kwargs):
        #see if the matrix is passing another matrix4d
        for entry in kwargs:
            formatentry = entry.lower()
            if formatentry=='base':
                other = kwargs[entry]
                valid4d = isinstance(other,Matrix4d)
                validmat3d = isinstance(other,Matrix3d)
                if(valid4d==True):
                    copy = kwargs[entry]
                    newmatrix = []
                    for r in range(copy.numrows()):
                        newcol = []
                        for c in range(copy.numcols()):
                            newcol.append(copy.matrix[r][c])
                        newmatrix.append(newcol)
                    super().__init__(direct=newmatrix)
                elif(validmat3d==True):
                    #see if its a vector or a full matrix
                    if other.numcols()==other.numrows():
                        #this means its square and we are good
                        super().__init__(direct=other.matrix)
                        #now add the extra entries
                        for r in range(self.numrows()):
                            self.matrix[r].append(0)
                        self.matrix.append([0,0,0,1])
                    elif other.numcols()==1:
                        #this means its a vector
                        super().__init__(direct=other.matrix)
                        self.matrix.append([1])
                    else:
                        raise('ill conditioned matrix for conversion to 4d')
                else:
                    raise('"base" keyword not existing 4d matrix or 3d matrix')                
            else:
                super().__init__(**kwargs)
    def trans_matrix(idist=0,jdist=0,kdist=0):
        '''
        This function returns a Matrix4d that performs the given transformation
        '''
        return Matrix4d(direct=[[1,0,0,idist],[0,1,0,jdist],[0,0,1,kdist],[0,0,0,1]])
    
    def rot_i_matrix(theta_i=0):
        '''
        This function returns a Matrix4d that would rotate a matrix theta_i
        radians about the i axis
        '''
        rotmatin = []
        rotmatin.append([1,0,0,0])
        rotmatin.append([0,math.cos(theta_i),(-1)*math.sin(theta_i),0])
        rotmatin.append([0,math.sin(theta_i),math.cos(theta_i),0])
        rotmatin.append([0,0,0,1])
        return Matrix4d(direct=rotmatin)
    def rot_j_matrix(phi_j=0):
        '''
        This function returns a Matrix4d that would rotate a matrix phi_j
        radians about the j axis
        '''
        rotmatin = []
        rotmatin.append([math.cos(phi_j),0,math.sin(phi_j),0])
        rotmatin.append([0,1,0,0])
        rotmatin.append([(-1)*math.sin(phi_j),0,math.cos(phi_j),0])
        rotmatin.append([0,0,0,1])
        return Matrix4d(direct=rotmatin)
    def rot_k_matrix(gamma_k=0):
        '''
        This function returns a Matrix4d that would rotate a matrix gamma_k
        radians about the k axis
        '''
        rotmatin = []
        rotmatin.append([math.cos(gamma_k),(-1)*math.sin(gamma_k),0,0])
        rotmatin.append([math.sin(gamma_k),math.cos(gamma_k),0,0])
        rotmatin.append([0,0,1,0])
        rotmatin.append([0,0,0,1])
        return Matrix4d(direct=rotmatin)
    def scale_matrix(scale=1):
        '''
        This function returns a Matrix4d that would scale the matrix
        by the the specified amount (1=100%, 2=200%, .5=50%,etc...)
        '''
        return Matrix4d(direct=[[scale,0,0,0],[0,scale,0,0],[0,0,scale,0],[0,0,0,1]])
        
class Vector3d(Matrix3d):
    '''
    This object represents a vector
    it may or may not carry a coordinate system
    '''
    
    def __init__(self,i,j,k,w=1):
        super().__init__(rows=4,cols=1)
        self.matrix[0][0] = i
        self.matrix[1][0] = j
        self.matrix[2][0] = k
        self.matrix[3][0] = w
        
    def unitvect(self):
        '''
        This returns a vector that is a unit vector of this vector
        (nothing changed in place)
        '''
        magn = self.mag()
        iunit = self.matrix[0][0]/magn
        junit = self.matrix[1][0]/magn
        kunit = self.matrix[2][0]/magn
        return Vector3d(iunit,junit,kunit)
        
    def mag(self):
        '''
        returns the magnitude of the vector
        '''
        return math.sqrt((self.dot(self)))
        
    def dot(self,vect):
        '''
        This function returns a dot product of two vectors
        '''
        validVector = isinstance(vect,Vector3d)
        if validVector==False:
            raise('Vector.dot requires a Vector3d as input')
        
        #all a dot product is, is an inner product of two vectors
        mytranspose = self.T()
        retval = (mytranspose*vect).matrix[0][0]
        #vect is 4d though and so the result must be subtracted by 1
        return retval-1
        
    def cross(self,vect):
        '''
        This function returns the cross product with the other vector
        '''
        validVector = isinstance(vect,Vector3d)
        if validVector==False:
            raise('Vector.cross requires a Vector3d as input')
        #if self.coord != vect.coord:
        #    raise('Vector.cross requires the same coordinate system')
        # generate a matrix with the vectors
        mat = Matrix3d(rows=3,cols=3)
        mat.matrix[0][0] = 1
        mat.matrix[0][1] = 1
        mat.matrix[0][2] = 1
        mat.matrix[1][0] = self.matrix[0][0]
        mat.matrix[1][1] = self.matrix[1][0]
        mat.matrix[1][2] = self.matrix[2][0]
        mat.matrix[2][0] = vect.matrix[0][0]
        mat.matrix[2][1] = vect.matrix[1][0]
        mat.matrix[2][2] = vect.matrix[2][0]
        
        #a cross product is just the cofactor of the matrix generated via
        #assembly of the above matrix
        
        ival = mat.cofac(0,0)
        jval = mat.cofac(0,1)
        kval = mat.cofac(0,2)
        return Vector3d(ival,jval,kval)
    
    def __sub__(self, other):
        '''
        this is mainly a pass through but we take the result and re-format the
        object
        '''
        mat3 = self-other
        return Vector3d(mat3.matrix[0][0],mat3.matrix[1][0],mat3.matrix[2][0])
    
    def __add__(self,other):
        '''
        this is mainly a pass through but we take the result and re-format the
        object
        '''
        mat3 = self+other
        return Vector3d(mat3.matrix[0][0],mat3.matrix[1][0],mat3.matrix[2][0])
    
    def __mul__(self,other):
        '''
        this is mainly a pass through but we take the result and re-format the
        object
        '''
        mat3 = self*other
        return Vector3d(mat3.matrix[0][0],mat3.matrix[1][0],mat3.matrix[2][0])

if __name__ == "__main__":
    
    matr1 = [[1,0,0],[0,1,0],[0,0,1]]
    matr2 = [[1],[0],[0]]
    testmatr1 = Matrix3d(direct = matr1)
    testmatr2 = Matrix3d(direct = matr2)
    #testmatr3 = Imatrix3d(rows=5,cols=5)
    vec1 = Vector3d(1,0,0)
    vec2 = Vector3d(0,1,0)
    vec3 = vec1.cross(vec2)
    #print(vec3)
    #print(testmatr3)
    #print(testmatr1)
    print(Matrix4d(base=testmatr2))
    
    #print(testmatr1.inv())
    #print(testmatr1*testmatr1.inv())
    #print(testmatr1.det())
    #print(testmatr1.cofac())
    #print(testmatr1.minor(0,1))
    #print(testmatr2)
    #print(testmatr1*testmatr2)
    
    