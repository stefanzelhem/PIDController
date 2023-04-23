class GameParameters:
      def __init__(self, p_factor,d_factor,i_factor,i_weight,sigma=0.0):
          self.p_factor=p_factor
          self.d_factor=d_factor
          self.i_factor=i_factor
          self.i_weight=i_weight
          self.sigma=sigma
          
class Var1Pars:
      def __init__(self, start,stop,num,var):
          self.start=start
          self.stop=stop
          self.num=num
          self.var=var
