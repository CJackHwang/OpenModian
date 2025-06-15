import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import static java.lang.Thread.sleep;

/**
 * @author zhangrui
 * @date 2020-04-04 19:08
 */
public class EveryProject {

    public  static List<String> contextId = new ArrayList<String>();

    public static void main(String[] args) throws Exception {
        getData();
//        for(String link : contextId){
//            System.out.println(link);
//        }
        getSchool();
    }

    public static void getData (){
        try {
            BufferedReader br = new BufferedReader(new InputStreamReader(new FileInputStream(new File("id.txt")),
                    "UTF-8"));
            String lineTxt = null;
            while ((lineTxt = br.readLine()) != null) {
                contextId.add("https://zhongchou.modian.com/item/"+lineTxt.trim()+".html");
            }
            br.close();
        } catch (Exception e) {
            System.err.println("read errors :" + e);
        }

    }

    public static void sleep58() throws InterruptedException {
        //创建Random类对象
        Random random = new Random();
        //产生随机数
        int number = random.nextInt(10000 -7000 + 1) + 7000;
        sleep(number);
    }

    public static void sleep24() throws InterruptedException {
        //创建Random类对象
        Random random = new Random();
        //产生随机数
        int number = random.nextInt(6000 - 4000 + 1) + 4000;
        sleep(number);
    }


    //爬取全部学院的url
    public static void getSchool() throws Exception {
        String path_out= "out.txt";   //自动生成的文件
        PrintStream ps = new PrintStream(path_out);
        System.setOut(ps);

        for(int index=0; index<contextId.size(); index++){
            if(index%9==0){
                sleep58();
                sleep24();
            }
            String url = contextId.get(index);
            // String url = "https://zhongchou.modian.com/item/834.html";
            Document doc = null;
            try {
                doc = Jsoup.connect(url).userAgent("Mozilla").get();
                Element listDiv = doc.getElementsByAttributeValue("class", "buttons clearfloat").first();

                //System.out.println(element);
                // System.out.println(listDiv.toString());
                String state = listDiv.toString();
                if(state.contains("众筹成功")){
                    String elementTitle = "不存在";
                    String elementContent = "不存在";
                    String elementUser = "不存在";
                    String elementLocation = "不存在";
                    String elementTag = "不存在";
                    String convertGoalMoney= "不存在";
                    String allMoney= "不存在";
                    String percent= "不存在";
                    String startTime= "不存在";
                    String endTime= "不存在";
                    String supportPeople= "不存在";
                    String convertNoMoneySupport= "不存在";


                    // System.out.println("众筹成功");
                    Element masthead = doc.getElementsByAttributeValue("class", "top-wrap clearfix").first();
                    elementTitle = masthead.select("h3[class]").first().select("span").first().text();

                    elementContent = masthead.getElementsByAttributeValue("id", "cont_match_short").first().text();

                    elementUser = masthead.select("span[data-nickname]").attr("data-nickname");

                    // Elements elementLocationTag = masthead.getElementsByAttributeValue("class","tags clearfix").select("span");
                    // System.out.println(elementLocationTag.toString());
                    elementLocation = masthead.getElementsByAttributeValue("class","tags clearfix").select("span").first().text();

                    elementTag = masthead.getElementsByAttributeValue("class","tags clearfix").select("span").last().text();

                    String goalMoney = masthead.getElementsByAttributeValue("class","goal-money").text();
                    convertGoalMoney = goalMoney.substring(goalMoney.indexOf("¥")+1);

                    allMoney = masthead.select("span[backer_money]").text();

                    percent = masthead.getElementsByAttributeValue("class","percent").text();

                    startTime = masthead.getElementsByAttributeValue("class","col2 remain-time").select("h3").attr("start_time");

                    endTime = masthead.getElementsByAttributeValue("class","col2 remain-time").select("h3").attr("end_time");

                    supportPeople = masthead.getElementsByAttributeValue("class","col3 support-people").select("span").text();

                    String noMoneySupport = doc.getElementsByAttributeValue("class","tit back-title clearfix").select("em").text();
                    convertNoMoneySupport = noMoneySupport.substring(noMoneySupport.indexOf("持")+1,noMoneySupport.indexOf("份")).trim();


                    System.out.println(url+"\t"+
                            "众筹成功"+"\t"+
                            elementTitle+"\t"+
                            elementUser+"\t"+
                            elementLocation+"\t"+
                            elementTag+"\t"+
                            convertGoalMoney+"\t"+
                            allMoney+"\t"+
                            percent+"\t"+
                            startTime+"\t"+
                            endTime+"\t"+
                            supportPeople+"\t"+
                            convertNoMoneySupport+"\t"+
                            elementContent+"\t"
                    );

                    sleep58();
                }
                else if(state.contains("众筹结束")){
                    String elementTitle = "不存在";
                    String elementContent = "不存在";
                    String elementUser = "不存在";
                    String elementLocation = "不存在";
                    String elementTag = "不存在";
                    String convertGoalMoney= "不存在";
                    String allMoney= "不存在";
                    String percent= "不存在";
                    String startTime= "不存在";
                    String endTime= "不存在";
                    String supportPeople= "不存在";
                    String convertNoMoneySupport= "不存在";


                    // System.out.println("众筹成功");
                    Element masthead = doc.getElementsByAttributeValue("class", "top-wrap clearfix").first();
                    elementTitle = masthead.select("h3[class]").first().select("span").first().text();

                    elementContent = masthead.getElementsByAttributeValue("id", "cont_match_short").first().text();

                    elementUser = masthead.select("span[data-nickname]").attr("data-nickname");

                    // Elements elementLocationTag = masthead.getElementsByAttributeValue("class","tags clearfix").select("span");
                    // System.out.println(elementLocationTag.toString());
                    elementLocation = masthead.getElementsByAttributeValue("class","tags clearfix").select("span").first().text();

                    elementTag = masthead.getElementsByAttributeValue("class","tags clearfix").select("span").last().text();

                    String goalMoney = masthead.getElementsByAttributeValue("class","goal-money").text();
                    convertGoalMoney = goalMoney.substring(goalMoney.indexOf("¥")+1);

                    allMoney = masthead.select("span[backer_money]").text();

                    percent = masthead.getElementsByAttributeValue("class","percent").text();

                    startTime = masthead.getElementsByAttributeValue("class","col2 remain-time").select("h3").attr("start_time");

                    endTime = masthead.getElementsByAttributeValue("class","col2 remain-time").select("h3").attr("end_time");

                    supportPeople = masthead.getElementsByAttributeValue("class","col3 support-people").select("span").text();

                    String noMoneySupport = doc.getElementsByAttributeValue("class","tit back-title clearfix").select("em").text();
                    convertNoMoneySupport = noMoneySupport.substring(noMoneySupport.indexOf("持")+1,noMoneySupport.indexOf("份")).trim();


                    System.out.println(url+"\t"+
                            "众筹失败"+"\t"+
                            elementTitle+"\t"+
                            elementUser+"\t"+
                            elementLocation+"\t"+
                            elementTag+"\t"+
                            convertGoalMoney+"\t"+
                            allMoney+"\t"+
                            percent+"\t"+
                            startTime+"\t"+
                            endTime+"\t"+
                            supportPeople+"\t"+
                            convertNoMoneySupport+"\t"+
                            elementContent+"\t"
                    );

                    sleep58();

                }else if(state.contains("看好创意")){
                    System.out.println(url+"\t"+ "看好创意"+ "\t");
                    sleep24();
                }else if(state.contains("立即购买支持")){
                    System.out.println(url+"\t"+ "众筹中"+ "\t");
                    sleep24();
                } else{
                    System.out.println(url+"\t"+ "不明情况"+ "\t");
                    sleep24();
                }


            } catch (Exception e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }



    }

}
