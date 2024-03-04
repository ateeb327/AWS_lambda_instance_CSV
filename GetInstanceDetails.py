import json
import boto3

def lambda_handler(event, context):
    instances = get_ec2_instances()

    html_response = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EC2 Instances</title>
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }

            th, td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }

            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <div class="header-row">
            <h2>EC2 Instances</h2>
            <button onclick="downloadCSV()">Download CSV</button>
        </div>
        <table id="instancesTable">
            <tr>
                <th>Name</th>
                <th>ID</th>
                <th>Public IP</th>
                <th>Key Pair</th>
            </tr>
    """

    for instance in instances:
        html_response += f"""
            <tr>
                <td>{instance['name']}</td>
                <td>{instance['id']}</td>
                <td>{instance['publicIp']}</td>
                <td>{instance['keyPair']}</td>
            </tr>
        """

    html_response += """
        </table>

        <script>
            function downloadCSV() {
                var csvContent = "data:text/csv;charset=utf-8,";
                csvContent += "Name,ID,Public IP,Key Pair\\n";

                var instances = """ + json.dumps(instances) + """;

                instances.forEach(function(instance) {
                    csvContent += instance.name + "," + instance.id + "," + instance.publicIp + "," + instance.keyPair + "\\n";
                });

                var encodedUri = encodeURI(csvContent);
                var link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", "ec2_instances.csv");
                document.body.appendChild(link);
                link.click();
            }
        </script>
    </body>
    </html>
    """

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': html_response
    }

def get_ec2_instances():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()

    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            name = 'N/A'
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name = tag['Value']

            key_pair_name = instance.get('KeyName', 'N/A')

            instances.append({
                'name': name,
                'id': instance['InstanceId'],
                'publicIp': instance.get('PublicIpAddress', 'N/A'),
                'keyPair': key_pair_name,
            })

    return instances

# For local testing, you can print the HTML response
if __name__ == '__main__':
    print(lambda_handler(None, None)['body'])
