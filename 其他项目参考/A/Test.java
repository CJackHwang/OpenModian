/**
 * @author zhangrui
 * @date 2020-04-04 17:32
 */

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import static java.lang.Thread.sleep;

public class Test {

    public  static List<String> contextId = new ArrayList<String>();

    public static void main(String[] args) throws Exception {
        getSchool();
    }

    public static void sleep36() throws InterruptedException {
        //创建Random类对象
        Random random = new Random();
        //产生随机数
        int number = random.nextInt(6000 - 3000 + 1) + 3000;
        sleep(number);
    }


    //爬取全部学院的url
    public static void getSchool() throws Exception {
        String path_out= "id.txt";   //自动生成的文件
        PrintStream ps = new PrintStream(path_out);
        System.setOut(ps);
        for(int i=1; i<=197; i++){
            String url = "https://zhongchou.modian.com/all/top_time/all/"+i;
            Document doc = null;
            try {
                doc = Jsoup.connect(url).userAgent("Mozilla").get();
                Elements listDiv = doc.getElementsByAttributeValue("class", "pc_ga_pro_index_16");
                for (Element element : listDiv) {
                    //System.out.println(element);
                    //Elements texts = element.getElementsByAttribute("data-pro-id");
                    String id = element.attr("data-pro-id");

                    System.out.println(id);


                }
            } catch (Exception e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
            sleep36();
        }
    }


}
