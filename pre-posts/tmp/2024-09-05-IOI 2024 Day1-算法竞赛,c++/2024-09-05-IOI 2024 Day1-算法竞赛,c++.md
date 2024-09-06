# IOI 2024 Day1

## T1 nile

### 大致题意

有 $n$ 个物品要过河，每个物品有三个参数 $w_i,a_i,b_i$。现在有一条船来运这些物品，规则如下：

1. 一次运一个物品，无任何限制，花费 $a_i$ 的代价。
2. 一次运两个物品 $i,j(i\neq j)$，要求满足 $\left|w_i-w_j\right|\le D$，花费 $b_i+b_j$ 的代价。

现在保证 $b_i<a_i$，并给出 $q$ 此询问，每次询问给出 $D$ 求所有物品过河的最小代价。

$n,q \le 10^5$

### 题解

Day1 签到题，先考虑对于单组询问如何做。由于 $b_i<a_i$ 恒成立，所以能配对就配对显然更优，如果我们按 $w_i$ 排序，那么根据间隔与 $D$ 的大小可以将整个序列分为若干段表示段内相邻的两个物品能同船。

如果段的长度是偶数，那么肯定能两两配对全部用 $b_i$，如果长度是奇数那么就要考虑让其中奇数个物品单独过河，讨论一下不难发现肯定是让一个物品单独过。那么我们就要求出所有可以单独过（不影响其他物品两两配对）的物品增量 $a_i-b_i$ 最小是多少。

不影响其他物品那就有两种情况：

1. 位置与左端点奇偶性相同，那么左右的长度仍为偶数可以配对。
2. 前一个和后一个的差也满足 $D$ 的限制，那么除去该物品整个段仍是连通的，那么就可以配对。

所以我们只需 $O(n)$ 扫一遍就可以得到单次询问的答案。

下面考虑多组询问，重新探究分段的过程，当 $D$ 足够大之后，整个序列都将是一段，那么就研究单个/一段物品合并的过程，发现每个间隔都会连接两段，那么我们只需把询问离线排序，再把间隔长度排序，依次加入并修改即可。

在合并段的同时维护上述两种可删点的信息，由于只需最小值直接取 $\min$ 即可。第一种按前后两个物品重量差排序一起修改。第二种考虑按奇偶位置处理最小值，然后区间直接合并。

复杂度 $O(n\log n)$。

```cpp
#include<bits/stdc++.h>
using namespace std;
#define ll long long
const int N=1e5+10;
int fa[N],mn[N],mn2[N][2],sz[N],n,q,tot;
struct node{
	int w,a,b;
}p[N],ask[N],dlt[N<<1];
bool cmp(node a,node b){return a.w==b.w?a.b>b.b:a.w<b.w;}
ll res;
int find(int x){return fa[x]==x?x:fa[x]=find(fa[x]);}
void add(int p1,int p2)
{
	if(p2==0)
	{
		int f=find(p1);
		if(sz[f]&1)res-=min(mn[f],mn2[f][f&1]);
		mn[f]=min(mn[f],p[p1].a-p[p1].b);
		if(sz[f]&1)res+=min(mn[f],mn2[f][f&1]);
	}
	else
	{
		int f1=find(p1),f2=find(p2);
		if(sz[f1]&1)res-=min(mn[f1],mn2[f1][f1&1]);
		if(sz[f2]&1)res-=min(mn[f2],mn2[f2][f2&1]);
		fa[f2]=f1;
		sz[f1]+=sz[f2];
		mn[f1]=min(mn[f1],mn[f2]);
		mn2[f1][0]=min(mn2[f1][0],mn2[f2][0]);
		mn2[f1][1]=min(mn2[f1][1],mn2[f2][1]);
		if(sz[f1]&1)res+=min(mn[f1],mn2[f1][f1&1]);
	}
	return;
}
std::vector<long long> calculate_costs( std::vector<int> W, std::vector<int> A, std::vector<int> B, std::vector<int> E)
{
	n=W.size();
	vector<ll>ans;
 	for(int i=1;i<=n;i++)p[i]={W[i-1],A[i-1],B[i-1]};
 	sort(p+1,p+n+1,cmp);
 	q=E.size();
 	for(int i=0;i<q;i++) ask[i+1]={E[i],i};
 	sort(ask+1,ask+q+1,cmp);
 	ans.resize(q);
 	for(int i=2;i<=n;i++) dlt[++tot]={p[i].w-p[i-1].w,i-1,i};
	for(int i=2;i<n;i++) dlt[++tot]={p[i+1].w-p[i-1].w,i,0};
	sort(dlt+1,dlt+tot+1,cmp);
	for(int i=1;i<=n+1;i++)
	{
		fa[i]=i;
		mn[i]=1e9;
		mn2[i][i&1]=p[i].a-p[i].b;
		mn2[i][(i&1)^1]=1e9;
		sz[i]=1;
	}
	for(int i=1;i<=n;i++) res+=p[i].a;
	for(int i=1,p=0;i<=q;i++)
	{
		while(p<tot&&dlt[p+1].w<=ask[i].w)
			p++, add(dlt[p].a,dlt[p].b);
		ans[ask[i].a]=res;
	}
 	return ans;
}
//int main()
//{
//	int n,q;
//	vector<int>W,A,B,E;
//	vector<ll>ans;
//	read(n);
//	for(int i=0;i<n;i++)
//	{
//		W.push_back(read<int>());
//		A.push_back(read<int>());
//		B.push_back(read<int>());
//	}
//	read(q);
//	for(int i=0;i<q;i++)E.push_back(read<int>());
//	ans=calculate_costs(W,A,B,E);
//	for(ll i:ans)write(i);
//	flushout();
//	return 0;
//}
```

## T2 message

### 大致题意

现有一个长 $S \ \text{bits}$ 的  