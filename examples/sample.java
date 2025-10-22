// Example Java code with issues

import java.io.*;

public class Calculator {
    private int result;
    
    // Missing null check
    public int divide(Integer a, Integer b) {
        return a / b;  // ArithmeticException if b is 0
    }
    
    // Resource leak
    public String readFile(String filename) {
        try {
            FileReader reader = new FileReader(filename);
            BufferedReader br = new BufferedReader(reader);
            return br.readLine();
            // Reader never closed!
        } catch (Exception e) {
            return null;
        }
    }
    
    // Security issue: SQL injection
    public void updateUser(String username, String email) {
        String query = "UPDATE users SET email='" + email + 
                      "' WHERE username='" + username + "'";
        // Execute query...
    }
}
