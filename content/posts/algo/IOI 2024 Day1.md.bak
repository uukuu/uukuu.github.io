---
title: IOI 2024 Day1
date: 2024-09-05 19:00:00
type: 
mathjax: true
tag: 
    - 算法竞赛
    - IOI
categories:
    - 算法竞赛
---


# IOI 2024 Day1

## T1 nile

### 大致题意

有 $n$ 个物品要过河，每个物品有三个参数 $w\_i,a\_i,b\_i$。现在有一条船来运这些物品，规则如下：

1. 一次运一个物品，无任何限制，花费 $a\_i$ 的代价。
2. 一次运两个物品 $i,j(i\neq j)$，要求满足 $\left|w\_i-w\_j\right|\le D$，花费 $b\_i+b\_j$ 的代价。

现在保证 $b\_i<a\_i$，并给出 $q$ 此询问，每次询问给出 $D$ 求所有物品过河的最小代价。

$n,q \le 10^5$

### 题解

Day1 签到题，先考虑对于单组询问如何做。由于 $b\_i<a\_i$ 恒成立，所以能配对就配对显然更优，如果我们按 $w\_i$ 排序，那么根据间隔与 $D$ 的大小可以将整个序列分为若干段表示段内相邻的两个物品能同船。

如果段的长度是偶数，那么肯定能两两配对全部用 $b\_i$，如果长度是奇数那么就要考虑让其中奇数个物品单独过河，讨论一下不难发现肯定是让一个物品单独过。那么我们就要求出所有可以单独过（不影响其他物品两两配对）的物品增量 $a\_i-b\_i$ 最小是多少。

不影响其他物品那就有两种情况：

1. 位置与左端点奇偶性相同，那么左右的长度仍为偶数可以配对。
2. 前一个和后一个的差也满足 $D$ 的限制，那么除去该物品整个段仍是连通的，那么就可以配对。

所以我们只需 $O(n)$ 扫一遍就可以得到单次询问的答案。

下面考虑多组询问，重新探究分段的过程，当 $D$ 足够大之后，整个序列都将是一段，那么就研究单个/一段物品合并的过程，发现每个间隔都会连接两段，那么我们只需把询问离线排序，再把间隔长度排序，依次加入并修改即可。

在合并段的同时维护上述两种可删点的信息，由于只需最小值直接取 $\min$ 即可。第一种按前后两个物品重量差排序一起修改。第二种考虑按奇偶位置处理最小值，然后区间直接合并，用并查集等操作维护即可。

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

### 题解

玄妙基环树

## T3 tree

这题部分分设置很好，跟着部分分一点点想就出来了，本文将从 $\text{sub1,4,5}$ 依次讲解直到正解。

本文我们对题目稍微修改，定义修改操作为，每个点花 $W\_i$ 的价格使得子树总和减一。

首先对于叶子有个显然的结论，为了使得总花费最少，每个叶子的初始权值肯定是 $L$。

### sub1

该点特殊性质为 $W\_{P\_i} \le W\_i$。

也就是说在满足子树内情况时，操作次数越少越好，因为到祖先操作会更优。

所以只需要 $\text{dfs}$ 一遍，每个点贪心修改最少次数即可。

### sub4

该点性质为 $W\_i=1$，那么仍满足 $\text{sub1}$ 的性质可以继续用上述贪心，但此时询问次数没有限制，所以我们需要一些优化。

再次观察整个问题，当 $W\_i=1$ 时我们只需关注整颗树的操作总次数。不难发现当某个点子树内的和不超过 $R$ 时，整颗子树没有点需要进行修改操作。

现在我们考虑根节点的操作，如果根节点总和没到 $R$ 那么整棵树都不需要操作，只用叶子的花费。

否则我们一定是在根节点操作若干次使得根节点的总和为 $R$。

为了得到总操作次数最少，我们先考虑一个必要条件。记叶子个数为 $cnt$ 那么整棵树的总和为 $cnt\times L$，而由于根的限制最大是 $R$，所以最少次数就是 $cnt\times L -R$。而进一步观察可以发现这个值一定能够取到，因为无论在哪个点操做都会使得总和减一，并且没有任何浪费。

所以对于这个子任务我们只需统计叶子个数，然后答案就是 $\max(0,cnt\times L -R)$。

### sub5

这个子任务我觉得是最重要的一个。

该子任务限制为 $W\_i \le 1$，与上一个任务的区别在于 $W\_i$ 可以取 $0$。

那么我们就来思考多了 $0$ 会有什么影响。

首先，我们就不能贪心的选择在父亲操作，但是由于这些点是 $0$，也就是说在这里操作没有任何影响，所以肯定是在 $W\_i=0$ 的点操作若干次使得子树和为 $L$，这样显然是不劣的。

那么对于 $0$ 的点，每个点的权值都将变为 $L$，应该不难发现这个点对之后的贡献与把这棵子树删了换成一个叶子没有任何区别。所以我们就可以基于 $0$ 点，将整棵树分成若干棵树，分别统计相应的叶子个数。

但现在求答案的方式就变了，因为我们会有若干个不同叶子个数，这个子任务到是还好，本质不同的叶子个数应该只有 $\sqrt{n}$ 种，直接暴力维护应该也能过。

我们现在就来考虑求答案如何优化，我们现在相当于求 $\sum\limits\_{i=1}^n leaf\_i\times \max(0,i\times L-R)$，其中 $leaf\_i$ 表示含有 $i$ 个叶子的树的数量。由于 $i\times L-R$ 的单调性，这个最大值显然是前面一段取 $0$，后面一段取 $i\times L -R$。所以我们只需要求出第一个取右边的 $i=\lceil\frac{R}{L}\rceil$，那么更大的 $i$ 肯定取的也是右侧，只需要维护后缀 $leaf\_i\times i$的和，还有后缀 $leaf\_i$ 的和即可。

### 无约束条件

在做完前面三个子任务后，最后一步已经不是很难了，只需要对做法进行优化。

我们只需考虑每一个 $W\_i$ 的贡献。具体的我们可以进行如下操作，当作子任务 5 求一次答案，然后将所有 $W\_i$ 减 $1$，并与 $0$ 取最大值。这本质上也是一种贪心，我们要考虑每个值被操作次数最少是多少，当一个点 $W\_i$ 减为 $0$ 后，就意味着在这个点操作肯定比没减到 $0$ 的点更优。

所以我们现在的问题就是对于每个 $1 \le j \le 10^6$，把 $W\_i<j$ 看作 $0$，$W\_i\ge j$ 看作 $1$，然后求出子任务 $5$ 中的 $leaf\_i$ 数组，并相应位置求和。

但是有 $q$ 次询问，不过仔细研究后，对于不同的 $L,R$ 我们在上述操作的过程中是完全一致的，所以我们只需预处理出 $leaf\_i$ 数组即可。

现在我们考虑如何求出 $leaf\_i$。发现在 $W\_i$ 减少过程中，每个点只会有一次对 $leaf\_i$ 的变化量有影响的操作，就是当 $W\_i$ 第一次减为 $0$ 的时候。

而如果当前最小的 $W\_i$ 记作 $W\_{min}$，那么在接下来 $W\_{min}$ 次减一操作中 $leaf\_i$ 的改变是相同的，可以考虑用差分。

不过正着删点并不好维护，我们考虑倒着往里面加点，这样就可以用并查集动态维护当前的连通块，及其叶子个数，同时用差分可以统计每个叶子个数的子树出现的总个数，具体细节请参考代码。

最后别忘了加上初始叶子的贡献。

```cpp
#include <bits/stdc++.h>
using namespace std;

const int N = 2e5 + 10;
int n, q, w[N], id[N], fa[N], fat[N], vis[N], sz[N];
long long sum[N], sum2[N], sumleaf;
vector<int> e[N];
bool cmp(int x, int y)
{
	return w[x] > w[y];
}
int find(int x)
{
	return fa[x] == x ? x : fa[x] = find(fa[x]);
}
void change(int now, int v, int val) //差分维护贡献，每个连通块出现时 + w_i，消失时 - w_i 
{
	sum[sz[now]] -= val;
	sz[now] += v;
	sum[sz[now]] += val;
	return;
}
void merge(int now, int fat, int val)
{
	int f = find(fat);
	fa[now] = f;
	sum[sz[now]] -= val; //删除被合并连通块的贡献 
	change(f, sz[now], val);
	return;
}
void del(int now)
{
	if (fat[now] && vis[fat[now]])  //当父亲已经在时，儿子会作为一个叶子被计算在父亲中，需减去贡献 
	{
		int f = find(fat[now]);
		change(f, -1, w[now]);
	}
	for (int to : e[now]) //儿子存在就和儿子合并，否则将儿子视作叶子 
		if (vis[to])
			merge(to, now, w[now]);
		else
			change(now, 1, w[now]);
	if (vis[fat[now]])
		merge(now, fat[now], w[now]);
	vis[now] = 1;
	return;
}
void init(std::vector<int> P, std::vector<int> W)
{
	n = P.size();
	for (int i = 1; i < n; i++)
		e[P[i] + 1].push_back(i + 1), fat[i + 1] = P[i] + 1;
	for (int i = 0; i < n; i++)
		w[i + 1] = W[i];
	for (int i = 1; i <= n; i++)
		if (e[i].size() == 0) //给叶子加个点，便于统一操作 
		{
			sumleaf += w[i];
			e[i].push_back(0);
		}
	//sz 表示每个连通块叶子个数 
	for (int i = 1; i <= n; i++)
		id[i] = i, fa[i] = i, sz[i] = 0, vis[i] = 0;
	sort(id + 1, id + n + 1, cmp);
	for (int i = 1; i <= n; i++)
		del(id[i]);
	for (int i = 1; i <= n; i++)
		sum2[i] = sum2[i - 1] + sum[i] * i, sum[i] += sum[i - 1];
	return;
}

long long query(int L, int R)
{
	int k = min((R - 1) / L + 1, n + 1);
	return (sum2[n] - sum2[k - 1]) * L - R * (sum[n] - sum[k - 1]) + sumleaf * L;
}
```


 