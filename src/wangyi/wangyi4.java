package wangyi;
import  java.util.*;
public class wangyi4 {
    public static void main(String[] args)
    {/*
        int x=zuijinBeishu(100,6);
        System.out.println(x);
*/

        Scanner sc=new Scanner(System.in);
        while(sc.hasNext())
        {
            int start=sc.nextInt();
            int end=sc.nextInt();
            int time=0;
            int num=1;
            List<Integer> citys=new ArrayList<>();
            if(start==end)
            {
                System.out.println(time);
                System.out.println(num);
                System.out.println(start);
                continue;
            }
            if(end%start==0||start%end==0)
            {
                System.out.println(time);
                System.out.println(2);
                System.out.println(start+" "+end);
                continue;
            }
            boolean flag=false;
            if(start>end)
            {
                int temp=end;
                end=start;
                start=temp;
                flag=true;
            }

            citys.add(start);
            int yinshu=zuijinInshu(end,start);
            int beishu=zuijinBeishu(end,start);
            int midway=0;
            if(Math.abs(yinshu-start)>Math.abs(beishu-end))
            {
                midway=beishu;
                time=Math.abs(beishu-end);
                if(beishu!=start&beishu!=end)
                    citys.add(midway);

            }
            else {
                midway=yinshu;
                time=Math.abs(yinshu-start);
                if(yinshu!=start&yinshu!=end)
                    citys.add(midway);
            }
            citys.add(end);
            if(flag)
                Collections.reverse(citys);
            System.out.println(time);
            System.out.println(citys.size());
            String strs="";
            for(int i=0;i<citys.size()-1;i++)
                strs+=String.valueOf(citys.get(i))+" ";
            System.out.println(strs+String.valueOf(citys.get(citys.size()-1)));
            /*
            if(midway==yinshu)
            {
                int tmp=yinshu-start;
                if(tmp>0)
                {
                    for(int i=start;i<=yinshu;i++)
                    {
                        citys.add(i);
                    }
                }
                else{
                    for(int i=yinshu;i<start;i++)
                    {
                        citys.add(i);
                    }
                }
                citys.add(end)
            }*/

        }
    }
    private static  int zuijinInshu(int a,int b)
    {
        int res=0;
        int min=Integer.MAX_VALUE;
        for(int i=1;i<a;i++)
        {
            int tmp=0;
            if(a%i==0)
            {
                if(Math.abs(b-i)<min)
                {
                    min=Math.abs(b-i);
                    res=i;
                }
            }

        }
        return res;
    }
    private static  int zuijinBeishu(int a,int b)
    {
        int beishu =a/b;
        int num1=a-beishu*b;
        int num2=(beishu+1)*b-a;
        if(num1>num2)
        {
            return (beishu+1)*b;
        }
        else return beishu*b;
    }

}
