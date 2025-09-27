from django.core.management.base import BaseCommand
from problems.models import GlobalTemplate


class Command(BaseCommand):
    help = '创建默认的全局代码模板'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Python基础模板',
                'language': 'python',
                'description': 'Python语言的基础算法模板，适用于大部分算法题',
                'template_code': '''# 读取输入
n = int(input())

# 处理逻辑
result = n

# 输出结果
print(result)'''
            },
            {
                'name': 'Python多行输入模板',
                'language': 'python',
                'description': '处理多行输入的Python模板',
                'template_code': '''# 读取第一行
n = int(input())

# 读取多行数据
data = []
for i in range(n):
    line = input().strip()
    data.append(line)

# 处理逻辑
result = len(data)

# 输出结果
print(result)'''
            },
            {
                'name': 'C++基础模板',
                'language': 'cpp',
                'description': 'C++语言的基础算法模板',
                'template_code': '''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    // 读取输入
    int n;
    cin >> n;
    
    // 处理逻辑
    int result = n;
    
    // 输出结果
    cout << result << endl;
    
    return 0;
}'''
            },
            {
                'name': 'C++竞赛模板',
                'language': 'cpp',
                'description': 'C++竞赛编程模板，包含常用头文件和优化',
                'template_code': '''#include <bits/stdc++.h>
using namespace std;

typedef long long ll;
typedef pair<int, int> pii;
typedef vector<int> vi;

#define FOR(i, a, b) for(int i = (a); i < (b); i++)
#define REP(i, n) FOR(i, 0, n)
#define pb push_back
#define mp make_pair

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    // 读取输入
    int n;
    cin >> n;
    
    // 处理逻辑
    int result = n;
    
    // 输出结果
    cout << result << endl;
    
    return 0;
}'''
            },
            {
                'name': 'C语言基础模板',
                'language': 'c',
                'description': 'C语言的基础算法模板',
                'template_code': '''#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // 读取输入
    int n;
    scanf("%d", &n);
    
    // 处理逻辑
    int result = n;
    
    // 输出结果
    printf("%d\\n", result);
    
    return 0;
}'''
            },
            {
                'name': 'Java基础模板',
                'language': 'java',
                'description': 'Java语言的基础算法模板',
                'template_code': '''import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        // 读取输入
        int n = sc.nextInt();
        
        // 处理逻辑
        int result = n;
        
        // 输出结果
        System.out.println(result);
        
        sc.close();
    }
}'''
            },
            {
                'name': 'JavaScript基础模板',
                'language': 'javascript',
                'description': 'JavaScript/Node.js的基础算法模板',
                'template_code': '''const readline = require('readline');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.on('line', (line) => {
    // 读取输入
    const n = parseInt(line);
    
    // 处理逻辑
    const result = n;
    
    // 输出结果
    console.log(result);
    
    rl.close();
});'''
            },
            {
                'name': 'Go语言基础模板',
                'language': 'go',
                'description': 'Go语言的基础算法模板',
                'template_code': '''package main

import (
    "fmt"
)

func main() {
    // 读取输入
    var n int
    fmt.Scanf("%d", &n)
    
    // 处理逻辑
    result := n
    
    // 输出结果
    fmt.Println(result)
}'''
            },
            {
                'name': 'Rust基础模板',
                'language': 'rust',
                'description': 'Rust语言的基础算法模板',
                'template_code': '''use std::io;

fn main() {
    // 读取输入
    let mut input = String::new();
    io::stdin().read_line(&mut input).expect("Failed to read line");
    let n: i32 = input.trim().parse().expect("Invalid number");
    
    // 处理逻辑
    let result = n;
    
    // 输出结果
    println!("{}", result);
}'''
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            template, created = GlobalTemplate.objects.get_or_create(
                name=template_data['name'],
                language=template_data['language'],
                defaults={
                    'template_code': template_data['template_code'],
                    'description': template_data['description'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 创建模板: {template.name}')
                )
            else:
                # 更新现有模板的代码和描述
                template.template_code = template_data['template_code']
                template.description = template_data['description']
                template.is_active = True
                template.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠ 更新模板: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ 完成! 创建了 {created_count} 个新模板，更新了 {updated_count} 个现有模板。'
            )
        )
        
        # 显示统计信息
        total_templates = GlobalTemplate.objects.count()
        active_templates = GlobalTemplate.objects.filter(is_active=True).count()
        languages = GlobalTemplate.objects.values_list('language', flat=True).distinct().count()
        
        self.stdout.write(f'\n📊 统计信息:')
        self.stdout.write(f'   总模板数: {total_templates}')
        self.stdout.write(f'   活跃模板: {active_templates}')
        self.stdout.write(f'   支持语言: {languages}')
