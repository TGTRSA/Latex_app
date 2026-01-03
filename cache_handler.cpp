#include <vector>
#include <string>
#include <algorithm>

struct Edit {
    enum Type { INSERT, DELETE, KEEP };
    Type type;
    char ch;
    int pos;
};

std::vector<Edit> computeDiff(const std::string& A, const std::string& B) {
    int n = A.size(), m = B.size();
    std::vector<std::vector<int>> dp(n + 1, std::vector<int>(m + 1));
    
    // Build LCS table
    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= m; j++) {
            if (i == 0 || j == 0)
                dp[i][j] = 0;
            else if (A[i-1] == B[j-1])
                dp[i][j] = dp[i-1][j-1] + 1;
            else
                dp[i][j] = std::max(dp[i-1][j], dp[i][j-1]);
        }
    }
    
    // Backtrack to find differences
    std::vector<Edit> edits;
    int i = n, j = m;
    while (i > 0 || j > 0) {
        if (i > 0 && j > 0 && A[i-1] == B[j-1]) {
            edits.push_back({Edit::KEEP, A[i-1], i-1});
            i--; j--;
        } else if (j > 0 && (i == 0 || dp[i][j-1] >= dp[i-1][j])) {
            edits.push_back({Edit::INSERT, B[j-1], i});
            j--;
        } else if (i > 0 && (j == 0 || dp[i][j-1] < dp[i-1][j])) {
            edits.push_back({Edit::DELETE, A[i-1], i-1});
            i--;
        }
    }
    
    std::reverse(edits.begin(), edits.end());
    return edits;
}
